class VCStatusScene extends Phaser.Scene {
    constructor() {
        super({ key: 'VCStatusScene', active: true });
        this.cpuUsage = 0;
        this.ramUsage = 0;
    }

    create() {
        this.cpuLabel = this.add.text(10, 10, 'CPU:', { fontSize: '18px', fill: '#0f0' });
        this.cpuBar = this.add.graphics();
        this.ramLabel = this.add.text(10, 40, 'RAM:', { fontSize: '18px', fill: '#0f0' });
        this.ramBar = this.add.graphics();

        // Listen for resource updates from the main game
        this.game.events.on('updateResources', (data) => {
            this.cpuUsage = data.cpu;
            this.ramUsage = data.ram;
            this.updateBars();
        });
    }

    updateBars() {
        this.cpuBar.clear();
        this.cpuBar.fillStyle(0x00ff00, 1);
        this.cpuBar.fillRect(60, 10, this.cpuUsage * 2, 20);
        if (this.cpuUsage > 80) {
            this.cpuBar.fillStyle(0xff0000, 1);
        }

        this.ramBar.clear();
        this.ramBar.fillStyle(0x00ff00, 1);
        this.ramBar.fillRect(60, 40, this.ramUsage * 2, 20);
        if (this.ramUsage > 80) {
            this.ramBar.fillStyle(0xff0000, 1);
        }
    }
}
