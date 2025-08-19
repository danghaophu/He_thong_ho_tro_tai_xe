const video = document.createElement('video');
video.setAttribute('autoplay', true);
video.setAttribute('muted', true);
video.setAttribute('playsinline', true);
document.body.appendChild(video);

navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  });

const canvas = document.createElement('canvas');

function updateStatus() {
  const ctx = canvas.getContext('2d');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(blob => {
    const formData = new FormData();
    formData.append('frame', blob, 'frame.jpg');

    fetch('/detect', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById('status').innerText = data.status;

      const now = new Date().toLocaleTimeString();
      const newRow = `<tr><td>${now}</td><td>${data.status}</td></tr>`;
      document.getElementById('log-body').insertAdjacentHTML('afterbegin', newRow);

      if (data.status.toLowerCase().includes('ngủ')) {
        drowsyTimestamps.push(Date.now());
        checkDrowsyEvents();
      }
    });
  }, 'image/jpeg');
}
