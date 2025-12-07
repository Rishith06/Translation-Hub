import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Full Screen Falling Stars with Vertical Credits", layout="wide")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
div[data-testid="stDecoration"] {visibility: hidden;}
.block-container {padding: 0; margin: 0;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>#credits-title { font-size: 2.5em !important; }</style>
<style>#credits-title { font-size: 2.5em !important; letter-spacing: 0.15em; }</style>

<style>
  html, body {
    margin: 0; padding: 0; height: 100%; width: 100%;
    overflow: hidden;
    background: linear-gradient(180deg, #0b0c2a, #1a1c40, #1e2b6f);
    font-family: 'Arial', sans-serif;
    color: white;
    position: relative;
  }
  .star {
    position: absolute;
    background: white;
    border-radius: 50%;
    opacity: 0.8;
    animation-name: fall;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
  }
  @keyframes fall {
    0% { transform: translateY(-10px); opacity: 1; }
    100% { transform: translateY(110vh); opacity: 0; }
  }

  /* Glowing effect only on the title */
  #credits-title {
    position: relative;
    font-weight: bold;
    font-size: 2em;
    margin-bottom: 10px;
    color: white;
    text-shadow:
      0 0 5px white,
      0 0 10px white,
      0 0 20px white,
      0 0 40px white;
    user-select: none;
    pointer-events: none;
  }

  #credits-container {
    position: fixed;
    top: 50%;
    left: 50%;
    width: 300px;
    height: 200px;
    transform: translate(-50%, -50%);
    overflow: visible;
    text-align: center;
  }

  #credits-list-wrapper {
    position: relative;
    width: 100%;
    height: 150px;
    overflow: hidden;
  }

  #credits-list {
    position: absolute;
    width: 100%;
    animation: scrollList 20s linear infinite;
    top: 130%;
    left: 0;

    /* Removed mask so no transparency fade */
    opacity: 1;
  }

  @keyframes scrollList {
    0% {
      top: 140%;
      opacity: 1;
    }
    100% {
      top: -200%;
      opacity: 1;
    }
  }
</style>
</head>
<body>
<script>
  const starCount = 150;
  for(let i=0; i<starCount; i++) {
    const star = document.createElement('div');
    star.classList.add('star');
    const size = Math.random() * 2 + 1;
    star.style.width = size + 'px';
    star.style.height = size + 'px';
    star.style.left = (Math.random() * 100) + 'vw';
    star.style.top = '-10px';
    star.style.animationDuration = (Math.random() * 5 + 3) + 's';
    star.style.animationDelay = (Math.random() * 5) + 's';
    document.body.appendChild(star);
  }
</script>

<div id="credits-container">
  <div id="credits-title">CREDITS</div>
  <div id="credits-list-wrapper">
    <div id="credits-list">
      <!-- Original content -->
      <p>Ramisetty Jithendra Kumar<br>
         23-5B2 - III CSE</p>
      <p></p>

      <p>Jani Rehan<br>
         23-587 - III CSE</p>
      <p></p>

      <p>Patnam Kannabhiram<br>
         22-5A7 - IV CSE</p>
      <br>

      <p><strong>TEAM LEAD</strong></p>
      
      <p>Raja Ram Rishith<br>
         23-5B1 - III CSE</p>
      <p></p>

      <p>PENNAR</p><br>

      <hr style="border: none; height: 2px; background: white; margin: 20px 0;">

        <!-- Duplicated content for smooth loop -->
      <p>Ramisetty Jithendra Kumar</p>
      <p>23-5B2 - III CSE</p>
      <p></p>

      <p>Jani Rehan</p>
      <p>23-587 - III CSE</p>
      <p></p>

      <p>Patnam Kannabhiram</p>
      <p>22-5A7 - IV CSE</p>

      <hr style="border: none; height: 2px; background: white; margin: 20px 0;">

      <p><strong>TEAM LEAD</strong></p>
      
      <p>Raja Ram Rishith</p>
      <p>23-5B1 - III CSE</p>
      <p></p>
    </div>
  </div>
</div>

</body>
</html>
"""

components.html(html_code, height=800, scrolling=False)

st.markdown(
    """
    <style>
    iframe { 
        position: fixed !important;
        top: 0; left: 0;
        width: 100% !important;
        height: 100% !important;
        border: none;
        z-index: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)