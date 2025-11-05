window.onload = function() {
    const config = {
        type: Phaser.AUTO,
        width: window.innerWidth,
        height: window.innerHeight,
        parent: 'game-container',
        scene: [MainMenuScene, LanScene, PvpScene, SettingsScene, NotepadScene, AccountScene, PremiumScene, VCStatusScene, ShopScene]
    };

    const game = new Phaser.Game(config);
};
