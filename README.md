**SFHS - QRAttendify**
=

→ **App still under development.** ←
## Features

- Advanced QR Scanning
- Students Registration & Automatic Emailing Generated QR
- Students List
- Editable Information of Students
- Secured
## The Diagram For QRAttendify

![QR Attendify Diagram - Final](https://github.com/CarlM-69/QRAttendify/assets/73862565/cc6d7f92-7074-4d75-ab7e-b79eab95d05c)

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`ATTENDANCE_DEV_SETUP_PASSWORD`
## Generate Resource Files

To convert *resources.qrc* into *resources.py*, you will need to run this command

`pyrcc5 -o ./Resources/resources.py ./Resources/resources.qrc`<br>

And then, edit the file in line 9<br>

`from PyQt5 import QtCore` to `from PyQt6 import QtCore`
## Authors

- Facebook: [@carlmathewgabay](https://www.facebook.com/carlmathewgabay)
