import React, { useState } from "react";
import "./styles.css";

const App = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [pdfUploaded, setPdfUploaded] = useState(false);
    const [uploadMessage, setUploadMessage] = useState("");

    const uploadPDF = async (event) => {
        const file = event.target.files[0];
        if (!file) {
            alert("Please select a PDF file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: formData
            });

            if (!response.ok) throw new Error("Failed to upload file.");
            const data = await response.json();
            setUploadMessage(data.message);
            setPdfUploaded(true);
        } catch (error) {
            console.error("File upload failed:", error);
            alert("File upload failed. Ensure the backend is running.");
        }
    };
    const sendMessage = async () => {
        if (!input.trim()) return;
        setMessages((prev) => [...prev, { text: input, sender: "user" }]);
        setInput("");
    
        try {
            const response = await fetch("http://127.0.0.1:5000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: input }), // Ensure correct format
            });
    
            const data = await response.json();
            if (response.ok) {
                setMessages((prev) => [...prev, { text: data.response, sender: "bot" }]);
            } else {
                console.error("Server Error:", data.error);
                alert("Server error: " + data.error);
            }
        } catch (error) {
            console.error("Chat request failed:", error);
            alert("Failed to get a response. Ensure the backend is running.");
        }
    };
    
    const handleKeyDown = (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    };

    return (
        <div className="container">
            <h2 className="header">Product Inquiry Chatbot</h2>
            <div className="upload-box">
                <input type="file" onChange={uploadPDF} />
                {uploadMessage && <p style={{ color: "green" }}>{uploadMessage}</p>}
            </div>
            <div className="chatbox">
                {messages.map((msg, index) => (
                    <div key={index} className={msg.sender === "user" ? "user-msg" : "bot-msg"}>
                        {msg.text}
                    </div>
                ))}
            </div>
            <div className="input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask about the product..."
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
};

export default App;