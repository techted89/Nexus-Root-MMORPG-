class IconFactory {
    static createIcon(scene, x, y, type, color = 0x00ff00) {
        const icon = scene.add.graphics({ x, y });

        switch (type) {
            case 'pc':
                this.drawPc(icon, color);
                break;
            case 'server':
                this.drawServer(icon, color);
                break;
            case 'firewall':
                this.drawFirewall(icon, color);
                break;
        }

        return icon;
    }

    static drawPc(icon, color) {
        icon.fillStyle(color, 1);
        icon.fillRect(0, 0, 32, 24); // Screen
        icon.fillRect(12, 26, 8, 4); // Stand
    }

    static drawServer(icon, color) {
        icon.fillStyle(color, 1);
        icon.fillRect(0, 0, 32, 12); // Server rack unit
        icon.fillStyle(0xcccccc, 1);
        icon.fillCircle(28, 6, 2); // Status light
    }

    static drawFirewall(icon, color) {
        icon.fillStyle(color, 1);
        icon.fillRect(0, 0, 32, 32); // Brick wall pattern
        icon.fillStyle(0x000000, 1);
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                if ((i + j) % 2 === 0) {
                    icon.fillRect(i * 8, j * 8, 8, 8);
                }
            }
        }
    }
}
