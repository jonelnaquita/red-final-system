const gradient = document.querySelector(".banner");

function onMouseMove(event) {
  gradient.style.backgroundImage = 'radial-gradient(at ' + event.clientX + 'px ' + event.clientY + 'px, rgba(255, 120, 120, 0.9) 0, #ffff 70%)';
}
document.addEventListener("mousemove", onMouseMove);