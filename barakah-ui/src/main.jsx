import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./styles.css";
import { consumeResetToken } from "./utils/resetToken.js";

const initialResetToken = consumeResetToken(window.location, window.history);
createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App initialResetToken={initialResetToken} />
  </React.StrictMode>,
);
