<!DOCTYPE html>
<html>
<body>
<script>
    const socket = new WebSocket("ws://127.0.0.1:8000/ws");

    socket.onopen = () => {
        console.log("Connected to server");
        socket.send("Hello from browser client!");
    };

    socket.onmessage = (event) => {
        console.log("Server:", event.data);
    };

    socket.onclose = () => {
        console.log("Connection closed");
    };
</script>
</body>
</html>
