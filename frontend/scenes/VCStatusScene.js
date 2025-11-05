class VCStatusScene extends Phaser.Scene {
    constructor() {
        super({ key: 'VCStatusScene', active: true });
        this.cpuUsage = 0;
        this.ramUsage = 0;
        this.credits = 0;
    }

    create() {
        this.traceCounter = this.add.text(10, 10, 'Trace: 0%', { fontSize: '16px', fill: '#0f0' });
        this.cpuLabel = this.add.text(150, 10, 'CPU: 0%', { fontSize: '16px', fill: '#0f0' });
        this.ramLabel = this.add.text(300, 10, 'RAM: 0%', { fontSize: '16px', fill: '#0f0' });
        this.creditsLabel = this.add.text(450, 10, 'Credits: 0', { fontSize: '16px', fill: '#0f0' });

        // Listen for resource updates from the main game
        this.game.events.on('updateResources', (data) => {
            this.cpuUsage = data.cpu;
            this.ramUsage = data.ram;
            this.credits = data.credits;
            this.updateText();
        });
    }

    updateText() {
        this.cpuLabel.setText(`CPU: ${this.cpuUsage}%`);
        this.ramLabel.setText(`RAM: ${this.ramUsage}%`);
        this.creditsLabel.setText(`Credits: ${this.credits}`);

        if (this.cpuUsage > 80) {
            this.cpuLabel.setFill('#ff0000');
        } else {
            this.cpuLabel.setFill('#0f0');
        }

        if (this.ramUsage > 80) {
            this.ramLabel.setFill('#ff0000');
        } else {
            this.ramLabel.setFill('#0f0');
        }
    }
}
