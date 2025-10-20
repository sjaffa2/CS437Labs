import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_blue_app/Utils.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'dart:convert';
import 'dart:typed_data';

import './ChatPage.dart';
import './StatusPage.dart';
import './NavigationPage.dart';

import 'package:permission_handler/permission_handler.dart';


class MainPage extends StatefulWidget {
  const MainPage();

  @override
  _MainPage createState() => new _MainPage();
}

class _MainPage extends State<MainPage> {
  int _currentPageIndex = 1;
  int _messageCounter = 0;

  // bluetooth
  BluetoothDevice? server;
  BluetoothConnection? connection;
  bool isConnecting = true;
  bool get isConnected => connection != null && connection!.isConnected;
  bool isDisconnecting = false;
  BluetoothDevice? _device;

  // messages
  List<Message> messages = [];
  String _messageBuffer = '';
  PiInfo _piInfo = PiInfo();

  @override
  void initState() {
    super.initState();
    requestBluetoothPermissions();

    FlutterBluetoothSerial.instance
        .getBondedDevices()
        .then((List<BluetoothDevice> bondedDevices) {
      setState(() {
        for(BluetoothDevice device in bondedDevices){
          if (device.name == "ray"){
            _device = device;
            server = device;
            break;
          }
        }
      });
    });
  }

  Future<void> requestBluetoothPermissions() async {
    final bluetoothStatus = await Permission.bluetoothConnect.status;
    final scanStatus = await Permission.bluetoothScan.status;
    final locationStatus = await Permission.location.status;

    if (!bluetoothStatus.isGranted || !scanStatus.isGranted || !locationStatus.isGranted) {
      Map<Permission, PermissionStatus> statuses = await [
        Permission.bluetoothConnect,
        Permission.bluetoothScan,
        Permission.location,
      ].request();

      if (statuses.values.any((status) => status.isDenied || status.isPermanentlyDenied)) {
        // Handle denial gracefully
        print('Some permissions denied. Bluetooth will not work.');
      } else {
        print('All Bluetooth permissions granted!');
      }
    } else {
      print('Bluetooth permissions already granted.');
    }
  }

  @override
  void dispose() {
    if (isConnected) {
      isDisconnecting = true;
      connection!.dispose();
      connection = null;
    }
    FlutterBluetoothSerial.instance.setPairingRequestHandler(null);
    super.dispose();
  }

  void _onMessageCountChanged(int value) {
    setState(() {
      _messageCounter = value;
    });
  }

  void _onSentMessage(int clientID, String text) {
    setState(() {
      messages.add(Message(clientID, text));
    });
  }

  void _connectBluetooth() {
    // if no server found, show notification and return
    if (server == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('No bonded device!'),
          duration: Duration(seconds: 2),
        ),
      );
      return;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text("Connecting to [${server?.name ?? 'Unknown'}]"),
        duration: Duration(seconds: 2),
      ),
    );

    BluetoothConnection.toAddress(server!.address).then((_connection) {
      print('Connected to the device');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Live chat with [${server?.name ?? 'Unknown'}]"),
          duration: Duration(seconds: 2),
        ),
      );
      setState(() {
        connection = _connection;
        isConnecting = false;
        isDisconnecting = false;
      });

      connection!.input?.listen(_onDataReceived)?.onDone(() {
        print('dummy message');
      });
    }).catchError((error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Cannot connect to [${server!.name}]"),
          duration: Duration(seconds: 2),
        ),
      );
      print('!!! Cannot connect, exception occured');
      // print(error);
    });
  }

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    final themeProvider = Provider.of<ThemeProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Lab1B'),
        shadowColor: theme.colorScheme.shadow,
        actions: <Widget>[
          IconButton(
            icon: const Icon(Icons.refresh_sharp),
            tooltip: 'Refresh data',
            onPressed: () {
              _sendMessage(PiConstants.all);
            },
          ),
          IconButton(
            icon: (isConnected) ? const Icon(Icons.bluetooth_connected) : const Icon(Icons.heart_broken),
            tooltip: 'Connect to bluez',
            onPressed: _connectBluetooth,
          ),
          IconButton(
            icon: const Icon(Icons.dark_mode),
            tooltip: 'Dark Mode',
            onPressed: themeProvider.toggleTheme,
          ),
        ]
      ),

      body: <Widget>[
        NavigationPage(
          connection: connection,
          onRefreshConnection: _connectBluetooth,
          piInfo: _piInfo,
        ),
        StatusPage(
          connection: connection,
          onRefreshConnection: _connectBluetooth,
          piInfo: _piInfo,
        ),
        ChatPage(
            connection: connection,
            onRefreshConnection: _connectBluetooth,
            isConnecting: isConnecting,
            messages: messages,
            onMessageCountChanged: _onMessageCountChanged,
            onSentMessage: _onSentMessage,
          ),
      ][_currentPageIndex],

      bottomNavigationBar: NavigationBar(
        onDestinationSelected: (int index) {
          setState(() {
            _currentPageIndex = index;
          });
          if (index == 2) {
            setState(() {
              _messageCounter = 0;
            });
          }
        },
        indicatorColor: Colors.white,
        selectedIndex: _currentPageIndex,
        destinations: <Widget>[
          NavigationDestination(
            icon: Icon(Icons.gps_fixed_sharp),
            label: 'Navigation',
          ),
          NavigationDestination(
            selectedIcon: Icon(Icons.home),
            icon: Icon(Icons.home_outlined),
            label: 'Home',
          ),
          NavigationDestination(
              icon: (_messageCounter <= 0) ? 
                Icon(Icons.messenger_sharp): 
                Badge(label: Text(_messageCounter.toString()), child: Icon(Icons.messenger_sharp)),
              label: 'Messages',
          ),
        ],
      ),
    );
  }


  void _onDataReceived(Uint8List data) {
    print(data);
    // Allocate buffer for parsed data
    int backspacesCounter = 0;
    data.forEach((byte) {
      if (byte == 8 || byte == 127) {
        backspacesCounter++;
      }
    });
    Uint8List buffer = Uint8List(data.length - backspacesCounter);
    int bufferIndex = buffer.length;

    // Apply backspace control character
    backspacesCounter = 0;
    for (int i = data.length - 1; i >= 0; i--) {
      if (data[i] == 8 || data[i] == 127) {
        backspacesCounter++;
      } else {
        if (backspacesCounter > 0) {
          backspacesCounter--;
        } else {
          buffer[--bufferIndex] = data[i];
        }
      }
    }

    // Create message if there is new line character
    String dataString = String.fromCharCodes(buffer);
    print(dataString);

    int index = buffer.indexOf(13);
    if (~index != 0) {
      String wholeMessage = backspacesCounter > 0
              ? _messageBuffer.substring(
                  0, _messageBuffer.length - backspacesCounter)
              : _messageBuffer + dataString.substring(0, index);
      if (looksLikeJson(wholeMessage)) {
        Map<String, dynamic> data = jsonDecode(wholeMessage);
        setState(() {
          _piInfo.assignFromJson(data);
          if (_piInfo.all == 0) {
            if (data.containsKey(PiConstants.battery)) messages.add(Message(1, "Battery is ${_piInfo.battery}${PiConstants.batterySuffix}"));
            if (data.containsKey(PiConstants.temperature)) messages.add(Message(1, "Temp is ${_piInfo.temperature}${PiConstants.temperatureSuffix}"));
            if (data.containsKey(PiConstants.speed)) messages.add(Message(1, "Speed is ${_piInfo.speed}${PiConstants.speedSuffix}"));
            if (data.containsKey(PiConstants.power)) messages.add(Message(1, "Power is ${_piInfo.power}${PiConstants.powerSuffix}"));
            if (data.containsKey(PiConstants.distance)) messages.add(Message(1, "Distance is ${_piInfo.distance}${PiConstants.distanceSuffix}"));
            if (data.containsKey(PiConstants.carDirection)) messages.add(Message(1, "Direction is ${_piInfo.carDirection}"));
          }
          messages.add(Message(1, _piInfo.message));
          _messageCounter += (_piInfo.all == 0 ? data.length-1 : 1);
        });
      } else {
        messages.add(Message(1, wholeMessage));
        setState(() {
          _messageCounter ++;
        });
      }
      _messageBuffer = dataString.substring(index);
    } else {
      _messageBuffer = (backspacesCounter > 0
          ? _messageBuffer.substring(
              0, _messageBuffer.length - backspacesCounter)
          : _messageBuffer + dataString);
    }
  }

  bool looksLikeJson(String input) {
  input = input.trim();
  return (input.startsWith('{') && input.endsWith('}')) ||
         (input.startsWith('[') && input.endsWith(']'));
  }

  void _sendMessage(String text) async {
    text = text.trim();
    if (text.length > 0) {
      try {
        connection!.output.add(Uint8List.fromList(utf8.encode(text)));
        await connection!.output.allSent;
      } catch (e) {
        setState(() {});
      }
    }
  }
}
