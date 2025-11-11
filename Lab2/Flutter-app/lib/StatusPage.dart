import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'package:flutter_blue_app/Utils.dart';

class StatusPage extends StatefulWidget {
  final BluetoothConnection? connection;
  final void Function() onRefreshConnection;
  final PiInfo piInfo;

  const StatusPage({
    Key? key,
    required this.connection,
    required this.onRefreshConnection,
    required this.piInfo,
  }) : super(key: key);


  @override
  State<StatusPage> createState() => _StatusPageState();
}

class _StatusPageState extends State<StatusPage> {
  bool get isConnected => widget.connection != null && widget.connection!.isConnected;

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GridView.count(
          crossAxisCount: 2,
          childAspectRatio: 1.77,
          scrollDirection: Axis.horizontal,
          children: [
            StatusCell(
              serviceName: 'Speed',
              value: widget.piInfo.speed,
              suffix: PiConstants.speedSuffix,
            ),
            StatusCell(
              serviceName: 'Power',
              value: widget.piInfo.power,
              suffix: PiConstants.powerSuffix,
            ),
            StatusCell(
              serviceName: 'Temp',
              value: widget.piInfo.temperature,
              suffix: PiConstants.temperatureSuffix,
            ),
            StatusCell(
              serviceName: 'Battery',
              value: widget.piInfo.battery,
              suffix: PiConstants.batterySuffix,
            ),
          ],
        );
  }
}

class StatusCell extends StatelessWidget {
  const StatusCell({
    Key? key,
    required this.serviceName,
    required this.value,
    required this.suffix,
  }) : super(key: key);

  final String serviceName;
  final String value;
  final String suffix;

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    final isDark = themeProvider.themeMode == ThemeMode.dark;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 2.0),
      decoration:  BoxDecoration(
        color: themeProvider.backgroundColor,
        borderRadius: isDark ? BorderRadius.circular(9) : BorderRadius.circular(6),
        boxShadow: isDark ? [
          BoxShadow(
            color: themeProvider.fontColor.withOpacity(0.8),
            blurRadius: 9,
            spreadRadius: 1,
            offset: Offset(0, 0),
          ),
        ] : [
          BoxShadow(
            color: themeProvider.fontColor.withOpacity(0.2),
            blurRadius: 5,
            offset: Offset(0, 0),
          )
        ],
        border: Border.all(color: themeProvider.fontColor, width: 0)
      ),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              serviceName,
              style: TextStyle(
                color: themeProvider.fontColor,
                fontSize: 24,
                fontWeight: FontWeight.bold,
                letterSpacing: 2,
              ),
            ),
            Text(
              (value == PiConstants.defaultValue) ? value: value+suffix,
              style: TextStyle(
                color: themeProvider.fontColor,
                fontSize: 24,
                fontWeight: FontWeight.bold,
                letterSpacing: 2,
              ),
            )
          ],
        )
      ),
    );
  }
}
