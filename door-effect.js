document.addEventListener('DOMContentLoaded', () => {
    const thumbTurn = document.getElementById('thumb-turn');
    const door = document.getElementById('door');
    const scene = document.querySelector('.scene');
    const lockBase = document.querySelector('.lock-base');

    setTimeout(() => {
        scene.classList.add('zoom-in');
        lockBase.classList.add('glint');

        setTimeout(() => {
            thumbTurn.classList.add('twist');

            setTimeout(() => {
                door.classList.add('open');
                scene.classList.add('door-is-open'); // ★追加: シーンを回転させるクラスを追加

                setTimeout(() => {
                    door.classList.remove('open');
                    thumbTurn.classList.remove('twist');
                    lockBase.classList.remove('glint');
                    scene.classList.remove('door-is-open'); // ★追加: シーンの回転を元に戻す

                    setTimeout(() => {
                        scene.classList.remove('zoom-in');
                    }, 1200);

                }, 4000);
            }, 400);
        }, 1000);
    }, 2000);
});