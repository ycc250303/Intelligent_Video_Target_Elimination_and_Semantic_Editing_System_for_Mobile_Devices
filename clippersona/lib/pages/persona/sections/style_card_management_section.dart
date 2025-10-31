import 'dart:io';
import 'package:flutter/material.dart';
import '../models/persona_models.dart';

class StyleCardManagementSection extends StatefulWidget {
  final List<StyleCard> styleCards;
  final Function(String cardId)? onDownload;
  final Function(String cardId)? onDelete;
  final Function(String cardId)? onShare;
  final Function(String cardId)? onUnshare;

  const StyleCardManagementSection({
    super.key,
    required this.styleCards,
    this.onDownload,
    this.onDelete,
    this.onShare,
    this.onUnshare,
  });

  @override
  State<StyleCardManagementSection> createState() =>
      _StyleCardManagementSectionState();
}

class _StyleCardManagementSectionState
    extends State<StyleCardManagementSection> {
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader('风格卡管理'),
        const SizedBox(height: 16),
        ...widget.styleCards.map((card) => _buildStyleCard(card)),
      ],
    );
  }

  Widget _buildSectionHeader(String title) {
    return Row(
      children: [
        Container(
          width: 4,
          height: 20,
          decoration: const BoxDecoration(
            color: Color(0xFF8B5CF6),
            borderRadius: BorderRadius.all(Radius.circular(2)),
          ),
        ),
        const SizedBox(width: 12),
        Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildStyleCard(StyleCard card) {
    return GestureDetector(
      onTap: () {
        // 点击卡片跳转到详情页
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => _buildDetailPage(card)),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF1F2937),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // 缩略图
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: const Color(0xFF374151),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: card.imageUrl.isEmpty
                      ? Image.asset(
                          'assets/communityPage/persona.png',
                          fit: BoxFit.cover,
                        )
                      : (card.imageUrl.startsWith('assets/')
                            ? Image.asset(card.imageUrl, fit: BoxFit.cover)
                            : Image.file(
                                File(card.imageUrl),
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) {
                                  return Image.asset(
                                    'assets/communityPage/persona.png',
                                    fit: BoxFit.cover,
                                  );
                                },
                              )),
                ),
              ),
              const SizedBox(width: 16),

              // 信息区域
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 标题和状态标签
                    Row(
                      children: [
                        Text(
                          card.title,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(width: 8),
                        _buildStatusBadge(card.status),
                      ],
                    ),
                    const SizedBox(height: 8),

                    // 操作按钮
                    _buildActionButtons(card),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 构建详情页面（复用社区详情页样式）
  Widget _buildDetailPage(StyleCard card) {
    // 转换为社区详情页需要的格式
    final personaData = {
      'title': card.title,
      'content': card.description.isEmpty
          ? '这是一个${card.status == StyleCardStatus.local ? "本地" : ""}风格卡。'
          : card.description,
      'image': card.imageUrl.isEmpty
          ? 'assets/communityPage/persona.png' // 默认风格卡图片
          : card.imageUrl,
      'likes': card.isShared ? card.comments : 0,
      'user': '我',
      'time': '刚刚',
    };

    return _StyleCardDetailPage(persona: personaData, styleCard: card);
  }

  /// 状态标签
  Widget _buildStatusBadge(StyleCardStatus status) {
    Color color;
    String text;

    switch (status) {
      case StyleCardStatus.local:
        color = const Color(0xFF6B7280);
        text = '本地';
        break;
      case StyleCardStatus.shared:
        color = const Color(0xFF10B981);
        text = '已共享';
        break;
      case StyleCardStatus.downloadable:
        color = const Color(0xFF3B82F6);
        text = '社区';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color, width: 1),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 11,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  /// 操作按钮
  Widget _buildActionButtons(StyleCard card) {
    return Row(
      children: [
        if (card.status == StyleCardStatus.local) ...[
          // 本地卡片：根据isShared显示不同按钮
          if (card.isShared) ...[
            // 已共享到社区：取消共享、删除
            _buildActionButton(
              label: '取消共享',
              icon: Icons.close,
              color: const Color(0xFFF59E0B), // 橙色
              onPressed: () {
                widget.onUnshare?.call(card.id);
              },
            ),
          ] else ...[
            // 未共享：共享到社区
            _buildActionButton(
              label: '共享到社区',
              icon: Icons.share,
              color: const Color(0xFF10B981), // 绿色
              onPressed: () {
                widget.onShare?.call(card.id);
              },
            ),
          ],
          const SizedBox(width: 8),
          _buildActionButton(
            label: '删除',
            icon: Icons.delete_outline,
            color: const Color(0xFFEF4444),
            onPressed: () {
              widget.onDelete?.call(card.id);
            },
          ),
        ] else if (card.status == StyleCardStatus.downloadable) ...[
          // 可下载卡片：下载
          Expanded(
            child: _buildActionButton(
              label: '下载',
              icon: Icons.download,
              color: const Color(0xFF3B82F6),
              onPressed: () {
                widget.onDownload?.call(card.id);
              },
            ),
          ),
        ] else if (card.status == StyleCardStatus.shared) ...[
          // 已共享卡片：编辑、取消共享
          _buildActionButton(
            label: '编辑',
            icon: Icons.edit,
            color: const Color(0xFF8B5CF6),
            onPressed: () {
              ScaffoldMessenger.of(
                context,
              ).showSnackBar(SnackBar(content: Text('编辑功能开发中：${card.title}')));
            },
          ),
          const SizedBox(width: 8),
          _buildActionButton(
            label: '取消共享',
            icon: Icons.close,
            color: const Color(0xFFF59E0B),
            onPressed: () {
              widget.onUnshare?.call(card.id);
            },
          ),
        ],
      ],
    );
  }

  /// 操作按钮组件
  Widget _buildActionButton({
    required String label,
    required IconData icon,
    required Color color,
    required VoidCallback onPressed,
  }) {
    return SizedBox(
      height: 32,
      child: ElevatedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon, size: 14),
        label: Text(label, style: const TextStyle(fontSize: 12)),
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        ),
      ),
    );
  }
}

// 风格卡详情页（复用社区详情页样式）
class _StyleCardDetailPage extends StatefulWidget {
  final Map<String, dynamic> persona;
  final StyleCard styleCard;

  const _StyleCardDetailPage({required this.persona, required this.styleCard});

  @override
  State<_StyleCardDetailPage> createState() => _StyleCardDetailPageState();
}

class _StyleCardDetailPageState extends State<_StyleCardDetailPage> {
  int _selectedTabIndex = 0;

  @override
  void initState() {
    super.initState();
    // 调试日志
    print('📄 打开风格卡详情页:');
    print('   标题: ${widget.styleCard.title}');
    print('   操作数: ${widget.styleCard.operations.length}');
    for (var i = 0; i < widget.styleCard.operations.length; i++) {
      print('   操作${i + 1}: ${widget.styleCard.operations[i].userInstruction}');
    }
  }

  Widget _buildOperationsList() {
    if (widget.styleCard.operations.isEmpty) {
      return Column(
        children: [
          Icon(Icons.inbox_outlined, size: 64, color: Colors.grey[600]),
          const SizedBox(height: 16),
          Text(
            '暂无记录的操作',
            style: TextStyle(color: Colors.grey[500], fontSize: 14),
          ),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '共记录 ${widget.styleCard.operations.length} 个操作',
          style: TextStyle(color: Colors.grey[400], fontSize: 12),
        ),
        const SizedBox(height: 12),
        ...widget.styleCard.operations.asMap().entries.map((entry) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    color: const Color(0xFF8B5CF6),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Center(
                    child: Text(
                      '${entry.key + 1}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF374151),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      entry.value.getDisplayText(),
                      style: const TextStyle(color: Colors.white, fontSize: 14),
                    ),
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: const Text('详情'),
        centerTitle: true,
        foregroundColor: Colors.white,
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.share, color: Colors.white),
            onPressed: () {
              // 处理分享
            },
          ),
          IconButton(
            icon: const Icon(Icons.more_vert, color: Colors.white),
            onPressed: () {
              // 处理更多操作
            },
          ),
        ],
      ),
      body: Container(
        height: MediaQuery.of(context).size.height,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/common/background.png'),
            fit: BoxFit.cover,
          ),
        ),
        child: Column(
          children: [
            SizedBox(
              height: MediaQuery.of(context).padding.top + kToolbarHeight,
            ),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    // 风格卡主卡片
                    Container(
                      margin: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.2),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(20),
                        child: Column(
                          children: [
                            // 图片区域
                            Stack(
                              children: [
                                Container(
                                  height: 200,
                                  child: ClipRRect(
                                    borderRadius: const BorderRadius.only(
                                      topLeft: Radius.circular(20),
                                      topRight: Radius.circular(20),
                                    ),
                                    child:
                                        widget.persona['image'] != null &&
                                            (widget.persona['image'] as String)
                                                .isNotEmpty
                                        ? ((widget.persona['image'] as String)
                                                  .startsWith('assets/')
                                              ? Image.asset(
                                                  widget.persona['image'],
                                                  fit: BoxFit.cover,
                                                  width: double.infinity,
                                                  height: 200,
                                                )
                                              : Image.file(
                                                  File(widget.persona['image']),
                                                  fit: BoxFit.cover,
                                                  width: double.infinity,
                                                  height: 200,
                                                  errorBuilder:
                                                      (
                                                        context,
                                                        error,
                                                        stackTrace,
                                                      ) {
                                                        return Image.asset(
                                                          'assets/communityPage/persona.png',
                                                          fit: BoxFit.cover,
                                                          width:
                                                              double.infinity,
                                                          height: 200,
                                                        );
                                                      },
                                                ))
                                        : Image.asset(
                                            'assets/communityPage/persona.png',
                                            fit: BoxFit.cover,
                                            width: double.infinity,
                                            height: 200,
                                          ),
                                  ),
                                ),
                                Container(
                                  height: 200,
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      begin: Alignment.topCenter,
                                      end: Alignment.bottomCenter,
                                      colors: [
                                        Colors.transparent,
                                        Colors.black.withOpacity(0.3),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            // 内容区域
                            Container(
                              padding: const EdgeInsets.all(20),
                              decoration: const BoxDecoration(
                                color: Color(0xFFE8F5E8),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          widget.persona['title'] ?? '风格卡',
                                          style: const TextStyle(
                                            fontSize: 24,
                                            fontWeight: FontWeight.bold,
                                            color: Color(0xFF2C3E50),
                                          ),
                                        ),
                                      ),
                                      Row(
                                        children: [
                                          const Icon(
                                            Icons.thumb_up,
                                            color: Color(0xFF8E44AD),
                                            size: 20,
                                          ),
                                          const SizedBox(width: 4),
                                          Text(
                                            '${widget.persona['likes']}',
                                            style: const TextStyle(
                                              color: Color(0xFF8E44AD),
                                              fontWeight: FontWeight.bold,
                                              fontSize: 16,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    widget.persona['content'],
                                    style: TextStyle(
                                      fontSize: 14,
                                      color: Colors.grey[600],
                                      height: 1.4,
                                    ),
                                  ),
                                  const SizedBox(height: 16),
                                  Row(
                                    children: [
                                      Text(
                                        '作者: ${widget.persona['user']}',
                                        style: TextStyle(
                                          fontSize: 12,
                                          color: Colors.grey[600],
                                        ),
                                      ),
                                      const SizedBox(width: 20),
                                      if (widget.styleCard.isShared)
                                        Text(
                                          '下载: ${widget.styleCard.downloads}',
                                          style: TextStyle(
                                            fontSize: 12,
                                            color: Colors.grey[600],
                                          ),
                                        ),
                                      const SizedBox(width: 20),
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
                      margin: const EdgeInsets.symmetric(horizontal: 20),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.3),
                        borderRadius: BorderRadius.circular(15),
                      ),
                      child: Column(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
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
                                    padding: const EdgeInsets.only(bottom: 8),
                                    decoration: BoxDecoration(
                                      border: Border(
                                        bottom: BorderSide(
                                          color: _selectedTabIndex == 0
                                              ? const Color(0xFF3498DB)
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
                                const SizedBox(width: 30),
                                GestureDetector(
                                  onTap: () {
                                    setState(() {
                                      _selectedTabIndex = 1;
                                    });
                                  },
                                  child: Container(
                                    padding: const EdgeInsets.only(bottom: 8),
                                    decoration: BoxDecoration(
                                      border: Border(
                                        bottom: BorderSide(
                                          color: _selectedTabIndex == 1
                                              ? const Color(0xFF3498DB)
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
                                const SizedBox(width: 30),
                                GestureDetector(
                                  onTap: () {
                                    setState(() {
                                      _selectedTabIndex = 2;
                                    });
                                  },
                                  child: Container(
                                    padding: const EdgeInsets.only(bottom: 8),
                                    decoration: BoxDecoration(
                                      border: Border(
                                        bottom: BorderSide(
                                          color: _selectedTabIndex == 2
                                              ? const Color(0xFF3498DB)
                                              : Colors.transparent,
                                          width: 2,
                                        ),
                                      ),
                                    ),
                                    child: Text(
                                      '记录的操作',
                                      style: TextStyle(
                                        color: _selectedTabIndex == 2
                                            ? Colors.white
                                            : Colors.grey[400],
                                        fontSize: 16,
                                        fontWeight: _selectedTabIndex == 2
                                            ? FontWeight.bold
                                            : FontWeight.normal,
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.all(20),
                            child: _selectedTabIndex == 0
                                ? Text(
                                    widget.persona['content'],
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 14,
                                      height: 1.6,
                                    ),
                                  )
                                : _selectedTabIndex == 1
                                ? Column(
                                    children: [
                                      const Text(
                                        '暂无评论',
                                        style: TextStyle(
                                          color: Colors.grey,
                                          fontSize: 14,
                                        ),
                                      ),
                                    ],
                                  )
                                : _buildOperationsList(),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 30),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
