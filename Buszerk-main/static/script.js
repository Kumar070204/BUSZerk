// Fetch AI response from backend
async function getAIResponse(prompt) {
  try {
    const response = await fetch("http://localhost:3001/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }),
    });
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.json();
    return data.text;
  } catch (error) {
    console.error("Error fetching AI response:", error);
    return "Sorry, I encountered an error. Please try again.";
  }
}

// Speech synthesis functions
let isMuted = false;

function speakText(text) {
  if (isMuted) return; // Don't speak if muted

  const speech = new SpeechSynthesisUtterance(text);
  speech.lang = 'en-US';
  speech.rate = 1;
  speech.pitch = 1;

  // Select a female voice (if available)
  const voices = window.speechSynthesis.getVoices();
  const femaleVoice = voices.find(voice => 
    voice.lang === 'en-US' && 
    (voice.name.toLowerCase().includes('female') || 
     voice.name.includes('Google US English') || // Common female voice
     voice.name.includes('Samantha') || // Example of a known female voice
     voice.name.includes('Microsoft Zira')) // Windows female voice
  );
  speech.voice = femaleVoice || voices[0]; // Fallback to first voice if no female found

  window.speechSynthesis.speak(speech);
}

function toggleMute() {
  isMuted = !isMuted;
  const muteButton = document.getElementById("mute-button");
  const icon = muteButton.querySelector("i");
  icon.className = isMuted ? "fas fa-volume-mute" : "fas fa-volume-up";
  if (isMuted) {
    window.speechSynthesis.cancel(); // Stop any ongoing speech
  }
}

// Add message to chat
function addMessage(message, isUser) {
  const chatMessages = document.getElementById("chat-messages");
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${isUser ? "user" : "bot"}`;
  messageDiv.textContent = message;
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  // Speak bot messages only
  if (!isUser) {
    speakText(message);
  }
}

// Handle user message
async function handleUserMessage(message) {
  addMessage(message, true);
  const loadingMessage = "Thinking...";
  addMessage(loadingMessage, false);

  const response = await getAIResponse(message);

  const chatMessages = document.getElementById("chat-messages");
  chatMessages.removeChild(chatMessages.lastChild);
  addMessage(response, false);
}

// Wait for DOM to be fully loaded
document.addEventListener("DOMContentLoaded", () => {
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");
  const voiceButton = document.getElementById("voice-button");
  const muteButton = document.getElementById("mute-button");
  const typingIndicator = document.querySelector('.typing-indicator');

  let recognition = null;
  let isListening = false;

  // Ensure voices are loaded before using them
  window.speechSynthesis.onvoiceschanged = () => {
    // Voices are now available
  };

  // Initialize speech recognition
  if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      userInput.value = transcript;
      stopListening();
      sendMessage();
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      stopListening();
    };

    recognition.onend = () => {
      stopListening();
    };
  }

  function startListening() {
    if (recognition) {
      recognition.start();
      isListening = true;
      voiceButton.classList.add('listening');
    }
  }

  function stopListening() {
    if (recognition) {
      recognition.stop();
      isListening = false;
      voiceButton.classList.remove('listening');
    }
  }

  if (!userInput || !sendButton || !muteButton) {
    console.error("Required elements not found in DOM");
    return;
  }

  const sendMessage = () => {
    const message = userInput.value.trim();
    if (message) {
      handleUserMessage(message);
      userInput.value = "";
    }
  };

  voiceButton.addEventListener('click', () => {
    if (!isListening) {
      startListening();
    } else {
      stopListening();
    }
  });

  sendButton.addEventListener("click", sendMessage);

  muteButton.addEventListener("click", toggleMute);

  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

  userInput.focus();
});