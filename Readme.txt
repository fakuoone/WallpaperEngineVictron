This is a bunch of code that allows you to integrate live data from your victron installation (requires a Modbus TCP master such as CerboGX) into your windows background.

This solution is not the cleanest possible, but it works an can be customized to the finest detail. This is how it works:

Web Server:
1. setting up your devices, their registers (from the Victron Modbus register excel) using a class as a simple data storage object
2. using the read_holding_registers() function, read each data point of each defined device and apply some optional formatting and adding additional calculated data points
3. add all data into dictionaries and format them to json spec
4. use a scheduler to loop through acquire_data() every x seconds
5. initialize a web server using http.server
6. react to incoming 'GET' requests by sending the json formatted data
(Almost all python code is unecessary, if you can access the ModbusTCP data through JavaScript in the browser, which I was unable to achieve.)

Web Client:
6. Using XMLHttRequest, the client accesses the web server via 'GET' requests. The response will be json data which can be unpacked in for loops
7. the data is used to feed html labels, that hold the data name and value (only the html structure and id tag need to be manually created according to the defined data structure in the Web Server)
8. css and some js is used to color and style the web page

9. Wallpaper Engine has the ability to display html files as a background in the wallpaper editor

10. a .bat-file + shortcut is used to launch main.py minimized (due to dual monitor setup the background is messed up on system start up, which is why wallpaper engine is started (which fixes the issue) and then closed again