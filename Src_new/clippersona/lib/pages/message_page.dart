import 'package:flutter/material.dart';

class MessagePage extends StatefulWidget {
  const MessagePage({super.key});

  @override
  State<MessagePage> createState() => _MessagePageState();
}

class _MessagePageState extends State<MessagePage> {
  final List<Map<String, dynamic>> _messages = [
    {'name': '张三', 'message': '你好，最近怎么样？', 'time': '10:30', 'unread': true},
    {'name': '李四', 'message': '明天一起吃饭吧', 'time': '09:15', 'unread': false},
    {'name': '王五', 'message': '项目进展如何？', 'time': '昨天', 'unread': true},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('消息'),
        foregroundColor: Colors.white,
        actions: [IconButton(icon: Icon(Icons.search), onPressed: () {})],
      ),
      body: ListView.builder(
        itemCount: _messages.length,
        itemBuilder: (context, index) {
          final message = _messages[index];
          return Card(
            margin: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: Colors.blue,
                child: Text(
                  message['name'][0],
                  style: TextStyle(color: Colors.white),
                ),
              ),
              title: Row(
                children: [
                  Text(
                    message['name'],
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  if (message['unread'])
                    Container(
                      margin: EdgeInsets.only(left: 8),
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: Colors.red,
                        shape: BoxShape.circle,
                      ),
                    ),
                ],
              ),
              subtitle: Text(message['message']),
              trailing: Text(
                message['time'],
                style: TextStyle(color: Colors.grey),
              ),
              onTap: () {
                // 处理消息点击
              },
            ),
          );
        },
      ),
    );
  }
}
