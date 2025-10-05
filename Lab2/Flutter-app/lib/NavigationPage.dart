import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import 'package:mjpeg_stream/mjpeg_stream.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'package:flutter_blue_app/Utils.dart';

class NavigationPage extends StatefulWidget {
  final BluetoothConnection? connection;
  final void Function() onRefreshConnection;
  final PiInfo piInfo;

  const NavigationPage({
    required this.connection,
    required this.onRefreshConnection,
    required this.piInfo,
  });

  @override
  _NavigationPage createState() => new _NavigationPage();
}

class _NavigationPage extends State<NavigationPage> {
  bool get isConnected => widget.connection != null && widget.connection!.isConnected;
  final String videoUrl = 'http://192.168.11.11:9000/mjpg'; 
  bool cameraOn = false;

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

    final themeProvider = Provider.of<ThemeProvider>(context);
    return MaterialApp(
      title: 'Video Demo',
      home: Scaffold(
        backgroundColor: themeProvider.backgroundColor,
        body: Column(
          children: [
            Flexible(
              flex: 10,
              child: Center(
                child: cameraOn? MJPEGStreamScreen(
                  streamUrl: videoUrl,
                  timeout: const Duration(seconds: 30),
                  showLiveIcon: true,
                  watermarkText: "PiCam",
                  showWatermark: true,
                  blurSensitiveContent: true,
                ) : Container(),
              ),
            ),
            Flexible(
              flex: 2,
              child: Column(
                children: [
                  Text(
                    "Car Direction: ${widget.piInfo.carDirection}",
                    softWrap: true, 
                    style: TextStyle(
                      color: themeProvider.fontColor,
                      fontSize: 12,
                      fontWeight: FontWeight.normal,
                      letterSpacing: 1,
                    ),
                  ),
                  Text(
                    "Distance traveled: ${widget.piInfo.distance} cm",
                    style: TextStyle(
                      color: themeProvider.fontColor,
                      fontSize: 12,
                      fontWeight: FontWeight.normal,
                      letterSpacing: 1,
                    ),
                  ),
                ],
              ),
            ),
            Flexible(
              flex: 13,
              child: Keyboard(onSetDirection: _sendMessage,),
            ),
          ],
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () {
            setState(() {
              cameraOn = !cameraOn;
            });
          },
          child: Icon(
            cameraOn? 
              Icons.visibility_sharp : 
              Icons.visibility_off_sharp,
          ),
        ),
      ),
    );
  }

  void _sendMessage(String text) async {
    text = text.trim();
    if (text.isNotEmpty) {
      try {
        widget.connection!.output.add(Uint8List.fromList(utf8.encode(text)));
        await widget.connection!.output.allSent;
      } catch (e) {
        print("Error while sending message in NavigationPage: ${e.toString()}");
      }
    }
  }
}


class ThemedIconButton extends StatelessWidget {
  final IconData icon;
  final String tooltip;
  final void Function(String dir) onSetDirection;
  final String direction;

  const ThemedIconButton({
    Key? key,
    required this.icon,
    required this.tooltip,
    required this.onSetDirection,
    required this.direction,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final ColorScheme colorScheme = Theme.of(context).colorScheme;
    return IconButton(
      icon: Icon(
        icon,
        color: colorScheme.onPrimary,
      ),
      tooltip: tooltip,
      onPressed: () { onSetDirection(direction); },
      style: ButtonStyle(
        backgroundColor: WidgetStatePropertyAll(colorScheme.shadow),
      ),
    );
  }
}

class Keyboard extends StatelessWidget {
  final void Function(String dir) onSetDirection;

  const Keyboard({
    Key? key,
    required this.onSetDirection,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        children: [
          Expanded(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                KeyboardEmptySpace(),
                Flexible(
                  flex: 2,
                  child: ThemedIconButton(
                    icon: Icons.arrow_upward_sharp,
                    tooltip: 'Move forward',
                    onSetDirection: onSetDirection,
                    direction: Direction.forward,
                  ),
                ),
                KeyboardEmptySpace(),
              ],
            ),
          ),
          Expanded(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ThemedIconButton(
                  icon: Icons.arrow_back_sharp,
                  tooltip: 'Move left',
                  onSetDirection: onSetDirection,
                  direction: Direction.left,
                ),
                ThemedIconButton(
                  icon: Icons.stop_sharp,
                  tooltip: 'Stop',
                  onSetDirection: onSetDirection,
                  direction: Direction.stop,
                ),
                ThemedIconButton(
                  icon: Icons.arrow_forward_sharp,
                  tooltip: 'Move right',
                  onSetDirection: onSetDirection,
                  direction: Direction.right,
                ),
              ],
            ),
          ),
          Expanded(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                KeyboardEmptySpace(),
                Flexible(
                  flex: 2,
                  child: 
                ThemedIconButton(
                  icon: Icons.arrow_downward_sharp,
                  tooltip: 'Move backward',
                  onSetDirection: onSetDirection,
                  direction: Direction.backward,
                ),
                ),
                KeyboardEmptySpace(),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class KeyboardEmptySpace extends StatelessWidget {
  const KeyboardEmptySpace({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    return Flexible(
        flex: 1,
        child: SizedBox(
          width: 400,
          height: 400,
          child: Container( color: themeProvider.backgroundColor),
        )
    );
  }
}
