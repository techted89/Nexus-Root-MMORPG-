window.onload = function() {
    const config = {
        type: Phaser.AUTO,
        width: window.innerWidth,
        height: window.innerHeight,
        parent: 'game-container',
        scene: [MainMenuScene, GameScene, LanScene, PvpScene, SettingsScene, NotepadScene]
    };

    const game = new Phaser.Game(config);
};
