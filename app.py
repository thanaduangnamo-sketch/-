<!DOCTYPE html>
<html lang="th">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            /* เปลี่ยนพื้นหลังเป็นไล่เฉดสีเขียวเข้ม */
            background: radial-gradient(circle, #064e3b 0%, #000000 100%);
            min-height: 100vh;
        }
    </style>
</head>

<body class="flex items-center justify-center p-5 text-white">

    <div
        class="w-full max-w-sm bg-zinc-900 p-8 rounded-3xl border border-emerald-900 shadow-[0_0_40px_rgba(16,185,129,0.2)] text-center">
        <h1 class="text-3xl font-black text-white mb-2">APK DOWNLOADER</h1>
        <p class="text-emerald-500 font-bold mb-8">แอปทำเล่น สนใจจัดได้เลย</p>

        <a id="followBtn" href="https://discord.gg/HM2B4jaz" target="_blank" onclick="unlockDownload()"
            class="block w-full bg-zinc-800 hover:bg-zinc-700 py-4 rounded-xl font-bold mb-4 border border-emerald-900 transition transform hover:scale-105">
            🔗 กดติดตาม Discord ก่อน
        </a>

        <a id="downloadBtn" href="http://127.0.0.1:5500/HOME%20.HTM"
            class="block w-full bg-gray-700 cursor-not-allowed py-4 rounded-xl font-bold transition opacity-60"
            onclick="return false;">
            ❌ ล็อกอยู่ (ต้องกดติดตามก่อน)
        </a>

        <p class="text-zinc-600 text-xs mt-6">กรุณากดติดตามเพื่อปลดล็อกลิงก์ดาวน์โหลด</p>
    </div>

    <script>
        function unlockDownload() {
            const btn = document.getElementById('downloadBtn');

            // หน่วงเวลา 800ms ให้เหมือนกำลังตรวจสอบ
            setTimeout(() => {
                btn.classList.remove('bg-gray-700', 'cursor-not-allowed', 'opacity-60');
                // เปลี่ยนเป็นสีเขียวมรกตเมื่อปลดล็อก
                btn.classList.add('bg-emerald-600', 'hover:bg-emerald-500', 'shadow-[0_0_15px_rgba(16,185,129,0.5)]');
                btn.innerText = "✅ ดาวน์โหลด APK ทันที!";
                btn.setAttribute("onclick", "");
            }, 800);
        }
    </script>
</body>

</html>