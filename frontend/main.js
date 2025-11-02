const config = {
    type: Phaser.AUTO,
    width: window.innerWidth,
    height: window.innerHeight,
    scene: [MainMenuScene, GameScene, LanScene, PvpScene, SettingsScene]
};

const game = new Phaser.Game(config);
