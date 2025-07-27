window.playAnimation = function () {
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
				scene.classList.add('door-is-open');

				setTimeout(() => {
					door.classList.remove('open');
					lockBase.classList.remove('glint');
					scene.classList.remove('door-is-open');

                        setTimeout(() => {
                            thumbTurn.classList.remove('twist');
                        }, 1300); 

					    setTimeout(() => {
					    	scene.classList.remove('zoom-in');
					    }, 1500);

				}, 5000);
			}, 400);
		}, 1000);
	}, 2000);
};
