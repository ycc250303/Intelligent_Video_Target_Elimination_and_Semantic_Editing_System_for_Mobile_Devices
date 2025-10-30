import 'package:flutter/material.dart';

class PersonaDetailPage extends StatefulWidget {
  final Map<String, dynamic> persona;

  const PersonaDetailPage({super.key, required this.persona});

  @override
  State<PersonaDetailPage> createState() => _PersonaDetailPageState();
}

class _PersonaDetailPageState extends State<PersonaDetailPage> {
  int _selectedTabIndex = 0; // 0: 关于它, 1: 评论

  Widget _buildCommentItem(String username, String content, String time) {
    return Container(
      padding: EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 15,
                backgroundColor: Color(0xFF3498DB),
                child: Text(
                  username[0],
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              SizedBox(width: 10),
              Expanded(
                child: Text(
                  username,
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Text(
                time,
                style: TextStyle(color: Colors.grey[400], fontSize: 12),
              ),
            ],
          ),
          SizedBox(height: 8),
          Text(
            content,
            style: TextStyle(color: Colors.white, fontSize: 14, height: 1.4),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: Text('详情'),
        centerTitle: true,
        foregroundColor: Colors.white,
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.share, color: Colors.white),
            onPressed: () {
              // 处理分享
            },
          ),
          IconButton(
            icon: Icon(Icons.more_vert, color: Colors.white),
            onPressed: () {
              // 处理更多操作
            },
          ),
        ],
      ),
      body: Container(
        height: MediaQuery.of(context).size.height,
        decoration: BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/common/background.png'),
            fit: BoxFit.cover,
          ),
        ),
        child: Stack(
          children: [
            Column(
              children: [
                // 为AppBar留出空间
                SizedBox(
                  height: MediaQuery.of(context).padding.top + kToolbarHeight,
                ),

                // 可滚动的内容区域
                Expanded(
                  child: SingleChildScrollView(
                    child: Column(
                      children: [
                        // 风格卡主卡片
                        Container(
                          margin: EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(20),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withValues(alpha: 0.2),
                                blurRadius: 20,
                                offset: Offset(0, 10),
                              ),
                            ],
                          ),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(20),
                            child: Column(
                              children: [
                                // 上半部分 - 图片区域（透明背景）
                                Container(
                                  height: 200,
                                  decoration: BoxDecoration(
                                    image: widget.persona['image'] != null
                                        ? DecorationImage(
                                            image: AssetImage(
                                              widget.persona['image'],
                                            ),
                                            fit: BoxFit.cover,
                                          )
                                        : null,
                                  ),
                                  child: Container(
                                    decoration: BoxDecoration(
                                      gradient: LinearGradient(
                                        begin: Alignment.topCenter,
                                        end: Alignment.bottomCenter,
                                        colors: [
                                          Colors.transparent,
                                          Colors.black.withValues(alpha: 0.3),
                                        ],
                                      ),
                                    ),
                                  ),
                                ),

                                // 下半部分 - 内容区域（浅绿色背景）
                                Container(
                                  padding: EdgeInsets.all(20),
                                  decoration: BoxDecoration(
                                    color: Color(0xFFE8F5E8), // 浅绿色
                                  ),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      // 标题和点赞
                                      Row(
                                        mainAxisAlignment:
                                            MainAxisAlignment.spaceBetween,
                                        children: [
                                          Expanded(
                                            child: Text(
                                              widget.persona['title'] ?? '搞笑弹幕',
                                              style: TextStyle(
                                                fontSize: 24,
                                                fontWeight: FontWeight.bold,
                                                color: Color(0xFF2C3E50),
                                              ),
                                            ),
                                          ),
                                          Row(
                                            children: [
                                              Icon(
                                                Icons.thumb_up,
                                                color: Color(0xFF8E44AD),
                                                size: 20,
                                              ),
                                              SizedBox(width: 4),
                                              Text(
                                                '${widget.persona['likes']}',
                                                style: TextStyle(
                                                  color: Color(0xFF8E44AD),
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 16,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ],
                                      ),

                                      SizedBox(height: 8),

                                      // 描述
                                      Text(
                                        widget.persona['content'],
                                        style: TextStyle(
                                          fontSize: 14,
                                          color: Colors.grey[600],
                                          height: 1.4,
                                        ),
                                      ),

                                      SizedBox(height: 16),

                                      // 元数据
                                      Row(
                                        children: [
                                          Text(
                                            '作者: ${widget.persona['user']}',
                                            style: TextStyle(
                                              fontSize: 12,
                                              color: Colors.grey[600],
                                            ),
                                          ),
                                          SizedBox(width: 20),
                                          Text(
                                            '下载: 1.2k',
                                            style: TextStyle(
                                              fontSize: 12,
                                              color: Colors.grey[600],
                                            ),
                                          ),
                                          SizedBox(width: 20),
                                          Text(
                                            '上传时间: ${widget.persona['time']}',
                                            style: TextStyle(
                                              fontSize: 12,
                                              color: Colors.grey[600],
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),

                        // 标签页区域
                        Container(
                          margin: EdgeInsets.symmetric(horizontal: 20),
                          decoration: BoxDecoration(
                            color: Colors.black.withValues(alpha: 0.3),
                            borderRadius: BorderRadius.circular(15),
                          ),
                          child: Column(
                            children: [
                              // 标签页头部
                              Container(
                                padding: EdgeInsets.symmetric(
                                  horizontal: 20,
                                  vertical: 15,
                                ),
                                child: Row(
                                  children: [
                                    GestureDetector(
                                      onTap: () {
                                        setState(() {
                                          _selectedTabIndex = 0;
                                        });
                                      },
                                      child: Container(
                                        padding: EdgeInsets.only(bottom: 8),
                                        decoration: BoxDecoration(
                                          border: Border(
                                            bottom: BorderSide(
                                              color: _selectedTabIndex == 0
                                                  ? Color(0xFF3498DB)
                                                  : Colors.transparent,
                                              width: 2,
                                            ),
                                          ),
                                        ),
                                        child: Text(
                                          '关于它',
                                          style: TextStyle(
                                            color: _selectedTabIndex == 0
                                                ? Colors.white
                                                : Colors.grey[400],
                                            fontSize: 16,
                                            fontWeight: _selectedTabIndex == 0
                                                ? FontWeight.bold
                                                : FontWeight.normal,
                                          ),
                                        ),
                                      ),
                                    ),
                                    SizedBox(width: 30),
                                    GestureDetector(
                                      onTap: () {
                                        setState(() {
                                          _selectedTabIndex = 1;
                                        });
                                      },
                                      child: Container(
                                        padding: EdgeInsets.only(bottom: 8),
                                        decoration: BoxDecoration(
                                          border: Border(
                                            bottom: BorderSide(
                                              color: _selectedTabIndex == 1
                                                  ? Color(0xFF3498DB)
                                                  : Colors.transparent,
                                              width: 2,
                                            ),
                                          ),
                                        ),
                                        child: Text(
                                          '评论',
                                          style: TextStyle(
                                            color: _selectedTabIndex == 1
                                                ? Colors.white
                                                : Colors.grey[400],
                                            fontSize: 16,
                                            fontWeight: _selectedTabIndex == 1
                                                ? FontWeight.bold
                                                : FontWeight.normal,
                                          ),
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),

                              // 内容区域
                              Container(
                                padding: EdgeInsets.all(20),
                                child: _selectedTabIndex == 0
                                    ? Text(
                                        '这是一个幽默活泼的风格卡，适合短视频和直播场景使用。设计灵感来源于网络梗图和用户互动习惯，能够快速引起观众共鸣，提升内容趣味性。经过测试，使用此风格卡的内容互动率提升30%，支持自定义弹幕模板和表情包组合。',
                                        style: TextStyle(
                                          color: Colors.white,
                                          fontSize: 14,
                                          height: 1.6,
                                        ),
                                      )
                                    : Column(
                                        children: [
                                          // 评论列表
                                          _buildCommentItem(
                                            '用户123',
                                            '这个风格卡真的很棒！用起来效果很好',
                                            '2小时前',
                                          ),
                                          SizedBox(height: 15),
                                          _buildCommentItem(
                                            '创意达人',
                                            '下载了，正在试用中，期待效果',
                                            '5小时前',
                                          ),
                                          SizedBox(height: 15),
                                          _buildCommentItem(
                                            '短视频爱好者',
                                            '设计很用心，细节处理得很好',
                                            '1天前',
                                          ),
                                          SizedBox(height: 15),
                                          _buildCommentItem(
                                            '直播主播',
                                            '已经在直播中使用了，观众反应很好',
                                            '2天前',
                                          ),
                                          SizedBox(height: 20),
                                          // 添加评论输入框
                                          Container(
                                            padding: EdgeInsets.symmetric(
                                              horizontal: 15,
                                              vertical: 10,
                                            ),
                                            decoration: BoxDecoration(
                                              color: Colors.white.withValues(
                                                alpha: 0.1,
                                              ),
                                              borderRadius:
                                                  BorderRadius.circular(25),
                                            ),
                                            child: Row(
                                              children: [
                                                Expanded(
                                                  child: TextField(
                                                    style: TextStyle(
                                                      color: Colors.white,
                                                    ),
                                                    decoration: InputDecoration(
                                                      hintText: '写下你的评论...',
                                                      hintStyle: TextStyle(
                                                        color: Colors.grey[400],
                                                      ),
                                                      border: InputBorder.none,
                                                    ),
                                                  ),
                                                ),
                                                Icon(
                                                  Icons.send,
                                                  color: Color(0xFF3498DB),
                                                  size: 20,
                                                ),
                                              ],
                                            ),
                                          ),
                                        ],
                                      ),
                              ),
                            ],
                          ),
                        ),

                        SizedBox(height: 30),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
