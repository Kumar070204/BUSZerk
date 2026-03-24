const express = require("express");
const { GoogleGenerativeAI } = require("@google/generative-ai");

const app = express();
app.use(express.json());

const cors = require("cors");
app.use(cors({
  origin: "*",
  methods: ["GET", "POST"],
  allowedHeaders: ["Content-Type"],
}));

// Replace with your actual Gemini API key
const apiKey = "AIzaSyB6emmMul4U5DcWeTclkWGubV2W3h6sMa0"; // Ensure this is your valid key
const genAI = new GoogleGenerativeAI(apiKey);

// System instruction to define chatbot behavior
const systemInstruction = `
You are 'Lea the AI', an intelligent chatbot assisting users with safety features in the Buszerk app. Your responsibilities include:

1️⃣ **Instant Complaint Registration:**  
   - Allow users to file complaints without calling the police.
   - Ask questions according to the FIR format  
   - Auto-fill details like location, bus number, time, and description.  
   - Categorize complaints into **theft, harassment, or other safety issues** and send them to authorities. 
   - As soon as you collect the information, give a response message that you have filed the complaint. 
   

2️⃣ **Feature Guide & Assistance:**  
   - Explain how to use app features (SOS, live tracking, fake call, safety ratings, etc.).  
   - Provide step-by-step instructions in a **simple and user-friendly** manner.  

3️⃣ **Real-Time Safety Insights:**  
   - Alert users about crime-prone areas and unsafe routes.  
   - Suggest safer alternative buses or stops based on AI analysis.  

4️⃣ **Emergency Support:**  
   - Guide users on what to do in an emergency.  
   - Offer quick commands to trigger the SOS button or alert contacts.  

Stay concise, clear, and supportive in responses, ensuring a smooth user experience.
Responses should be user-friendly.
`;

app.post("/api/chat", async (req, res) => {
  const { prompt } = req.body;
  console.log("Received prompt:", prompt);

  if (!prompt) {
    console.error("No prompt provided");
    return res.status(400).json({ text: "No prompt provided" });
  }

  try {
    console.log("Calling Gemini API...");
    const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

    // Combine system instruction with user prompt
    const fullPrompt = `${systemInstruction}\n\nUser: ${prompt}`;
    const result = await model.generateContent(fullPrompt);
    const response = await result.response;
    const text = response.text();
    console.log("Gemini API response:", text);
    
    // Send text along with a flag for text-to-speech
    res.json({ text, speakText: true });

  } catch (error) {
    console.error("Gemini API Error:", error.message);
    console.error("Full error:", error);
    res.status(500).json({ text: "Server error: Unable to process request" });
  }
});

app.use(express.static(__dirname));

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});