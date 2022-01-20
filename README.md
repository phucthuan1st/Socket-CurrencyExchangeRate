# SOCKET PROGRAMMING
# LẬP TRÌNH SOCKET - TRA CỨU TIỀN TỆ
# FIT@HCMUS

## Contributer:
* Nguyễn Phúc Thuần
* Lê Trương Kinh Thành
* Tô Trần Sơn Bá

## API: [vAPI Appmob](https://vapi.vnappmob.com/api/v2/exchange_rate)
### [Document](https://vapi-vnappmob.readthedocs.io/en/latest/exchange_rate.v2.html)
### [Get API Key](https://vapi.vnappmob.com/api/request_api_key?scope=exchange_rate)
> Notice that the api_key will be expired by default after 15 days, so you will need to get new API Key automacally.
> You can follow these code to automacally update your data:
```python
        #get API key automacally
        url = "https://vapi.vnappmob.com/api/request_api_key?scope=exchange_rate"
        API_key_request_data = requests.get(url).json()
        API_key = API_key_request_data["results"]

        #use API key get in above to request data
        url = "https://vapi.vnappmob.com/api/v2/exchange_rate/bid?api_key="
        request_url = url + str(API_key)
        recieve = requests.get(request_url).json()
```
> The data will be dumped into a json file

## Special Thanks to:
* Mr. Lê Hà Minh
* Mr. Nguyễn Thanh Quân
* Mrs. Chung Thùy Linh

## Contact for work:
* Nguyễn Phúc Thuần: [Email](phucthuan.work@gmail.com), [Facebook](https://www.facebook.com/phucthuan95), [Github](https://github.com/phucthuan1st/)
* Lê Trương Kinh Thành: [Email](letruongkinhthanh@gmail.com), [Facebook](https://www.facebook.com/kinhthanh.letruong.3), [Github](https://github.com/KinhThanh38/)
* Tô Trần Sơn Bá: [Email](sonba4102@gmail.com), [Facebook](https://www.facebook.com/ba.tran.2002)

## Libraries used:
* [Tkinter](https://docs.python.org/3/library/tkinter.html)
* [Datetime](https://docs.python.org/3/library/datetime.html)
* [request](https://docs.python-requests.org/en/latest/)
* [Schedule](https://schedule.readthedocs.io/en/stable/)
* [Threading](https://docs.python.org/3/library/threading.html)
* [json](https://docs.python.org/3/library/json.html)
* [socket](https://docs.python.org/3/library/socket.html)

## Documentaries:
* [Tài liệu Socket Python](https://drive.google.com/file/d/1A1IsrfZuzOxfEaW3ukxblOfVYUmG1T8i/view)
* [Tài liệu Socket](https://drive.google.com/file/d/10lBDAwpoKDvZSqYgrrjKAqupyov44pEJ/view)
* [Basic Winsock Application](https://docs.microsoft.com/en-us/windows/win32/winsock/creating-a-basic-winsock-application)
* [Socket C++ Programming Introduction](https://www.youtube.com/watch?v=41XxeYkLAOk&feature=youtu.be)
* [Lập trình Socket - Mrs. Chung Thùy Linh](https://www.youtube.com/watch?v=OHW8OiO5v8U)
* [Socket Programming in Python GeeksForGeeks](https://www.geeksforgeeks.org/socket-programming-python/)
* [Codemy.com Tkinter](https://www.youtube.com/watch?v=yQSEXcf6s2I&list=PLCC34OHNcOtoC6GglhF3ncJ5rLwQrLGnV)
* [Basic Python client socket example](https://stackoverflow.com/questions/7749341/basic-python-client-socket-example)
* [Lập trình Socket - Đức Hiếu](https://www.youtube.com/playlist?list=PLF5iDxYhcQyf19PKUm4vi9jDp5OByF5Wt)
* [Login and Registration - Python Tkinter](https://www.youtube.com/watch?v=NAwcl9R0M9w)

## More about this project
We build this project in two months, so it have some bugs and feature that we can do better, so if we have time, we will update it carefully.
If you fork or clone this repository, please keep our credit as a reference for your stuff.
This project is done by FIT@HCMUS students.

### This project is only used for educational activities, commercial activities are prohibited
