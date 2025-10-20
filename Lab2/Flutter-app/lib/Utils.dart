import 'package:flutter/material.dart';

class ThemeProvider with ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.dark;
  Color _fontColor = ColorConstants.darkFontColor;
  Color _backgroundColor = ColorConstants.darkBackgroundColor;

  ThemeMode get themeMode => _themeMode;
  Color get fontColor => _fontColor;
  Color get backgroundColor => _backgroundColor;

  void toggleTheme() {
    _themeMode = _themeMode == ThemeMode.light ? ThemeMode.dark : ThemeMode.light;
    _fontColor = _themeMode == ThemeMode.light ? ColorConstants.lightFontColor : ColorConstants.darkFontColor;
    _backgroundColor = _themeMode == ThemeMode.light ? ColorConstants.lightBackgroundColor : ColorConstants.darkBackgroundColor;
    notifyListeners();
  }
}

class Message {
  int whom;
  String text;

  Message(this.whom, this.text);
}

class ColorConstants {
  static const Color darkFontColor = Colors.cyanAccent;
  static const Color lightFontColor = Colors.black;
  static const Color darkBackgroundColor = Colors.black;
  static const Color lightBackgroundColor = Color.fromARGB(232, 255, 255, 255);
}

class Direction {
  static const String forward = 'dir.f';
  static const String backward = 'dir.b';
  static const String left = 'dir.l';
  static const String right = 'dir.r';
  static const String stop = 'dir.s';
}

class PiConstants {
  static const String battery = 'battery';
  static const String temperature = 'temperature';
  static const String speed = 'speed';
  static const String power = 'power';
  static const String distance = 'distance';
  static const String carDirection = 'dir';
  static const String message = 'message';
  static const String all = 'all';

  static const String batterySuffix = '%';
  static const String temperatureSuffix = '°C';
  static const String speedSuffix = 'cm/s';
  static const String powerSuffix = '%';
  static const String distanceSuffix = 'cm';

  static const String defaultCarDirection = 'Unknown direction, it is running rogue!';
  static const String defaultMessage = 'No message from Ray.';
  static const String defaultValue = 'N/A';
}


class PiInfo {
  String battery;
  String temperature;
  String speed;
  String power;
  String distance;
  String carDirection;
  String message;
  int all;

  PiInfo({
    this.battery = PiConstants.defaultValue, 
    this.temperature = PiConstants.defaultValue, 
    this.speed = PiConstants.defaultValue, 
    this.power = PiConstants.defaultValue, 
    this.distance = PiConstants.defaultValue, 
    this.carDirection = PiConstants.defaultCarDirection, 
    this.message = PiConstants.defaultMessage, 
    this.all = 0
  });

  void assignFromJson(Map<String, dynamic> json) {
      json.forEach((key, value) {
        if (key == PiConstants.battery) {
          battery = value.toString();
        } else if (key == PiConstants.temperature) {
          temperature = value.toString();
        } else if (key == PiConstants.speed) {
          speed = value.toString();
        } else if (key == PiConstants.power) {
          power = value.toString();
        } else if (key == PiConstants.distance) {
          distance = value.toString();
        } else if (key == PiConstants.carDirection) {
          carDirection = value.toString();
        } else if (key == 'message') {
          message = value.toString();
        } else if (key == 'all') {
          all = json['all'] is int ? json['all'] as int : 0;
        }
      },);
      if (!json.containsKey('all')) {
        all = 0;
      }
  }

  @override
  String toString() {
    return '''
PiInfo {
  battery: $battery, 
  temperature: $temperature, 
  speed: $speed, 
  power: $power, 
  distance: $distance, 
  direction: $carDirection
}
    ''';
  }
}