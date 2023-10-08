import socket
import ssl

class URL:
    def __init__(self, url, encoding="utf-8") -> None:
        self.encoding = encoding
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"], \
            "Unsupported URL scheme: " + self.scheme
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        self.path = "/" + url

    def request(self):
        # utf-8, ISO-8859-1
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        headers = {"Host": self.host, "Connection": "close"}
        formatted_headers = "".join("{}: {}\r\n\r\n".format(k, v) for k, v in headers.items())
        print(formatted_headers)
        

        s.send(("GET {} HTTP/1.0\r\n".format(self.path) + formatted_headers).encode("utf-8"))
        # s.send(("GET {} HTTP/1.0\r\n".format(self.path) + \
        #         "Host: {}\r\n\r\n".format(self.host)).encode("utf-8") + \
        #         "Connection: close\r\n\r\n".encode("utf-8"))

        # response = s.makefile("r", newline="\r\n")
        response = s.makefile("r", encoding=self.encoding, newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        assert status == "200", "{}: {}".format(status, explanation)
        headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            headers[header.lower()] = value.strip()

        assert "transfer-encoding" not in headers
        assert "content-encoding" not in headers
       
        body = response.read()
        s.close()
        return headers, body
    
def show(body):
    in_angle = False
    for c in body:
        if c == "<":
            in_angle = True
        elif c == ">":
            in_angle = False
        elif not in_angle:
            print(c, end="")

def load(url):
    headers, body = url.request()
    show(body)

def headers(url):
    headers, body = url.request()
    print(headers)


if __name__ == "__main__":
    import sys
    if len(sys.argv)>2:
        load(URL(sys.argv[1], sys.argv[2]))
    else:
        headers(URL(sys.argv[1]))