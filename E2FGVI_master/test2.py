# -*- coding: utf-8 -*-
import cv2
from PIL import Image
import numpy as np
import importlib
import os
import argparse
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib import animation
import torch

from core.utils import to_tensors

# sample reference frames from the whole video
def get_ref_index(f, neighbor_ids, length):
    ref_index = []
    if num_ref == -1:
        for i in range(0, length, ref_length):
            if i not in neighbor_ids:
                ref_index.append(i)
    else:
        start_idx = max(0, f - ref_length * (num_ref // 2))
        end_idx = min(length, f + ref_length * (num_ref // 2))
        for i in range(start_idx, end_idx + 1, ref_length):
            if i not in neighbor_ids:
                if len(ref_index) > num_ref:
                    break
                ref_index.append(i)
    return ref_index

# 读帧方式
def read_frame_from_videos(video_path):
    frames = []
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    while success:
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        frames.append(image)
        success, image = vidcap.read()
        count += 1
    return frames


# 读取掩膜
def read_mask(mpath, size):
    masks = []
    mnames = os.listdir(mpath)
    mnames.sort()
    for mp in mnames:
        m = Image.open(os.path.join(mpath, mp))
        m = m.resize(size, Image.NEAREST)
        m = np.array(m.convert('L'))
        m = np.array(m > 0).astype(np.uint8)
        m = cv2.dilate(m,
                       cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3)),
                       iterations=4)
        masks.append(Image.fromarray(m * 255))
    return masks

# resize frames
def resize_frames(frames, size=None):
    if size is not None:
        frames = [f.resize(size) for f in frames]
    else:
        size = frames[0].size
    return frames, size



def main_worker():
    # 从用户输入获取视频和掩膜路径
    video_path = input("请输入视频文件的路径：")
    mask_path = input("请输入掩膜文件夹的路径：")
    
    # 用户选择模型
    model_choice = input("请选择模型类型 (e2fgvi/e2fgvi_hq):")
    
    # 读取视频帧
    frames = read_frame_from_videos(video_path)
    
    # 获取视频帧的尺寸
    size = frames[0].size
    
    # 创建设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net = importlib.import_module('model.' + model_choice)
    model = net.InpaintGenerator().to(device)
    
    # 加载权重（请根据自己的需要调整路径）
    ckpt_path = input("请输入模型检查点的路径：")
    data = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(data)
    #print(f'Loading model from: {args.ckpt}')
    model.eval()

    args.use_mp4 = True if args.video.endswith('.mp4') else False
    print(
        f'Loading videos and masks from: {args.video} | INPUT MP4 format: {args.use_mp4}'
    )
    frames = read_frame_from_videos(args)
    frames, size = resize_frames(frames, size)
    h, w = size[1], size[0]
    video_length = len(frames)
    imgs = to_tensors()(frames).unsqueeze(0) * 2 - 1
    frames = [np.array(f).astype(np.uint8) for f in frames]

    
    # 读取掩膜
    masks = read_mask(mask_path, size)
    binary_masks = [np.expand_dims((np.array(m) != 0).astype(np.uint8), 2) for m in masks]
    masks = to_tensors()(masks).unsqueeze(0)
    
    # 将图像转换为tensor
    imgs, masks = imgs.to(device), masks.to(device)
    comp_frames = [None] * video_length

    # 其他处理...
    print(f'Start test...') 
    for f in tqdm(range(0, video_length, neighbor_stride)):
        neighbor_ids = [
            i for i in range(max(0, f - neighbor_stride),
                             min(video_length, f + neighbor_stride + 1))
        ]
        ref_ids = get_ref_index(f, neighbor_ids, video_length)
        selected_imgs = imgs[:1, neighbor_ids + ref_ids, :, :, :]
        selected_masks = masks[:1, neighbor_ids + ref_ids, :, :, :]
        with torch.no_grad():
            masked_imgs = selected_imgs * (1 - selected_masks)
            mod_size_h = 60
            mod_size_w = 108
            h_pad = (mod_size_h - h % mod_size_h) % mod_size_h
            w_pad = (mod_size_w - w % mod_size_w) % mod_size_w
            masked_imgs = torch.cat(
                [masked_imgs, torch.flip(masked_imgs, [3])],
                3)[:, :, :, :h + h_pad, :]
            masked_imgs = torch.cat(
                [masked_imgs, torch.flip(masked_imgs, [4])],
                4)[:, :, :, :, :w + w_pad]
            pred_imgs, _ = model(masked_imgs, len(neighbor_ids))
            pred_imgs = pred_imgs[:, :, :h, :w]
            pred_imgs = (pred_imgs + 1) / 2
            pred_imgs = pred_imgs.cpu().permute(0, 2, 3, 1).numpy() * 255
            for i in range(len(neighbor_ids)):
                idx = neighbor_ids[i]
                img = np.array(pred_imgs[i]).astype(
                    np.uint8) * binary_masks[idx] + frames[idx] * (
                        1 - binary_masks[idx])
                if comp_frames[idx] is None:
                    comp_frames[idx] = img
                else:
                    comp_frames[idx] = comp_frames[idx].astype(
                        np.float32) * 0.5 + img.astype(np.float32) * 0.5

    # saving videos
    print('Saving videos...')
    save_dir_name = 'results'
    ext_name = '_results.mp4'
    save_base_name = args.video.split('/')[-1]
    save_name = save_base_name.replace(
        '.mp4', ext_name) if args.use_mp4 else save_base_name + ext_name
    if not os.path.exists(save_dir_name):
        os.makedirs(save_dir_name)
    save_path = os.path.join(save_dir_name, save_name)
    writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*"mp4v"),
                             default_fps, size)
    for f in range(video_length):
        comp = comp_frames[f].astype(np.uint8)
        writer.write(cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))
    writer.release()
    print(f'Finish test! The result video is saved in: {save_path}.')

    # show results
    print('Let us enjoy the result!')
    fig = plt.figure('Let us enjoy the result')
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.axis('off')
    ax1.set_title('Original Video')
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.axis('off')
    ax2.set_title('Our Result')
    imdata1 = ax1.imshow(frames[0])
    imdata2 = ax2.imshow(comp_frames[0].astype(np.uint8))

    def update(idx):
        imdata1.set_data(frames[idx])
        imdata2.set_data(comp_frames[idx].astype(np.uint8))

    fig.tight_layout()
    anim = animation.FuncAnimation(fig,
                                   update,
                                   frames=len(frames),
                                   interval=50)
    plt.show()


if __name__ == '__main__':
    main_worker()
