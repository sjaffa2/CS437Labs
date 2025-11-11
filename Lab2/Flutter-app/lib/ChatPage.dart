import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'package:flutter_blue_app/Utils.dart';

class ChatPage extends StatefulWidget {
  final BluetoothConnection? connection;
  final void Function() onRefreshConnection;
  final bool isConnecting;
  final List<Message> messages;
  final void Function(int value) onMessageCountChanged;
  final void Function(int clientID, String text) onSentMessage;

  const ChatPage({
    required this.connection,
    required this.onRefreshConnection,
    required this.isConnecting,
    required this.messages,
    required this.onMessageCountChanged,
    required this.onSentMessage,
  });

  @override
  _ChatPage createState() => new _ChatPage();
}

class _ChatPage extends State<ChatPage> {
  static final clientID = 0;
  bool get isConnected => widget.connection != null && widget.connection!.isConnected;

  final TextEditingController textEditingController = new TextEditingController();
  final ScrollController listScrollController = new ScrollController();

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.connection == null || !isConnected) {
      return Center(
          child: IconButton(
                iconSize: 72,
                icon: const Icon(Icons.refresh_sharp),
                tooltip: 'Refresh bluez connection',
                onPressed: widget.onRefreshConnection,
              ),
        );
    }

    final List<Row> list = widget.messages.map((_message) {
      return Row(
        children: <Widget>[
          Container(
            child: Text(
                (text) {
                  return text == '/shrug' ? '¯\\_(ツ)_/¯' : text;
                }(_message.text.trim()),
                style: TextStyle(color: Colors.white)),
            padding: EdgeInsets.all(12.0),
            margin: EdgeInsets.only(bottom: 8.0, left: 8.0, right: 8.0),
            width: 222.0,
            decoration: BoxDecoration(
                color:
                    _message.whom == clientID ? Colors.blueAccent : Colors.grey,
                borderRadius: BorderRadius.circular(7.0)),
          ),
        ],
        mainAxisAlignment: _message.whom == clientID
            ? MainAxisAlignment.end
            : MainAxisAlignment.start,
      );
    }).toList();

    return SafeArea(
        child: Column(
          children: <Widget>[
            Flexible(
              child: ListView(
                  padding: const EdgeInsets.all(12.0),
                  controller: listScrollController,
                  children: list),
            ),
            Row(
              children: <Widget>[
                Flexible(
                  child: Container(
                    margin: const EdgeInsets.only(left: 16.0),
                    child: TextField(
                      onTap:() => widget.onMessageCountChanged(0),
                      onTapOutside:(event) => widget.onMessageCountChanged(0),
                      style: const TextStyle(fontSize: 15.0),
                      controller: textEditingController,
                      decoration: InputDecoration.collapsed(
                        hintText: widget.isConnecting
                            ? 'Wait until connected...'
                            : isConnected
                                ? 'Type your message...'
                                : 'Chat got disconnected',
                        hintStyle: const TextStyle(color: Colors.grey),
                      ),
                      enabled: isConnected,
                    ),
                  ),
                ),
                Container(
                  margin: const EdgeInsets.all(8.0),
                  child: IconButton(
                      icon: const Icon(Icons.send),
                      onPressed: isConnected
                          ? () => _sendMessage(textEditingController.text)
                          : null),
                ),
              ],
            )
          ],
        ),
      );
  }

  void _sendMessage(String text) async {
    text = text.trim();
    textEditingController.clear();

    if (text.length > 0) {
      try {
        widget.connection!.output.add(Uint8List.fromList(utf8.encode(text)));
        await widget.connection!.output.allSent;

        widget.onSentMessage(clientID, text);

        Future.delayed(Duration(milliseconds: 333)).then((_) {
          listScrollController.animateTo(
              listScrollController.position.maxScrollExtent,
              duration: Duration(milliseconds: 333),
              curve: Curves.easeOut);
        });

      } catch (e) {
        // Ignore error, but notify state
        setState(() {});
      }
    }
  }
}
