class LanScene extends Phaser.Scene {
    constructor() {
        super({ key: 'LanScene' });
    }

    create() {
        this.add.text(100, 50, 'LAN Tree Chart', { fontSize: '32px', fill: '#0f0' });

        this.input.on('drag', (pointer, gameObject, dragX, dragY) => {
            gameObject.x = dragX;
            gameObject.y = dragY;
        });

        const backButton = this.add.text(this.cameras.main.width - 150, 50, 'Back to Menu', { fontSize: '24px', fill: '#0f0' })
            .setOrigin(0.5)
            .setInteractive();
        backButton.on('pointerdown', () => {
            window.removeEventListener('commandSuccess', this.handleCommandSuccess);
            this.scene.start('MainMenuScene');
        });

        this.graphContainer = this.add.container(0, 0);

        this.handleCommandSuccess = (event) => {
            this.fetchGameState('test_user');
            this.handleCommandResponse(event.detail);
        };
        window.addEventListener('commandSuccess', this.handleCommandSuccess);

        this.fetchGameState('test_user');
    }

    async fetchGameState(playerName) {
        try {
            const response = await fetch(`/api/player/${playerName}/state`);
            const data = await response.json();
            if (data.success) {
                this.graphContainer.removeAll(true);
                this.renderGraph(data.data.active_missions[0]);
            }
        } catch (error) {
            console.error('Error fetching game state:', error);
        }
    }

    renderGraph(mission) {
        let x = 150;
        let y = 200;

        // Player PC
        const playerNode = this.createNode(x, y, { type: 'pc', name: 'Your PC' });

        // Mission nodes
        let previousNode = playerNode;
        mission.nodes.forEach((nodeData, index) => {
            x += 150;
            const node = this.createNode(x, y, nodeData);
            this.drawConnection(previousNode, node);
            previousNode = node;

            if (nodeData.children) {
                const children = nodeData.children.map((childData, childIndex) => {
                    const childNode = this.createNode(x + 100, y + 100 + (childIndex * 100), childData);
                    childNode.setVisible(false);
                    this.drawConnection(node, childNode);
                    return childNode;
                });
                node.setData('children', children);
            }
        });
    }

    createNode(x, y, nodeData) {
        const icon = IconFactory.createIcon(this, 0, 0, nodeData.type);
        const label = this.add.text(0, 40, nodeData.name, { fontSize: '16px', fill: '#0f0' }).setOrigin(0.5);
        const node = this.add.container(x, y, [icon, label]);
        node.setSize(64, 64);
        node.setInteractive();
        this.input.setDraggable(node);
        node.setData('nodeData', nodeData);

        node.on('pointerdown', (pointer) => {
            if (pointer.rightButtonDown()) {
                this.showContextMenu(pointer, node);
            } else {
                if (node.getData('children')) {
                    node.getData('children').forEach(child => {
                        child.setVisible(!child.visible);
                    });
                }
            }
        });

        return node;
    }

    drawConnection(nodeA, nodeB) {
        const graphics = this.add.graphics();
        graphics.lineStyle(2, 0x00ff00, 1);
        this.graphContainer.add(graphics);
    }

    showContextMenu(pointer, node) {
        if (this.contextMenu) {
            this.contextMenu.destroy();
        }

        const nodeData = node.getData('nodeData');
        const commands = ['scan', 'ping', 'connect']; // Example commands

        const menu = this.add.container(pointer.x, pointer.y);
        const background = this.add.graphics();
        background.fillStyle(0x000000, 0.8);
        background.fillRect(0, 0, 150, commands.length * 30 + 10);
        menu.add(background);

        let y = 10;
        commands.forEach(command => {
            const commandText = this.add.text(10, y, command, { fontSize: '18px', fill: '#0f0' }).setInteractive();
            commandText.on('pointerdown', () => {
                const terminalInput = document.getElementById('input');
                terminalInput.value = `${command} ${nodeData.name}`;
                this.contextMenu.destroy();
            });
            menu.add(commandText);
            y += 30;
        });

        this.contextMenu = menu;
    }

    showInspectorPanel(nodeData) {
        if (this.inspectorPanel) {
            this.inspectorPanel.destroy();
        }

        const panel = this.add.container(this.cameras.main.width - 350, 100);
        const background = this.add.graphics();
        background.fillStyle(0x000000, 0.8);
        background.fillRect(0, 0, 300, 400);
        panel.add(background);

        let y = 20;
        const title = this.add.text(150, y, nodeData.name, { fontSize: '24px', fill: '#0f0' }).setOrigin(0.5);
        panel.add(title);

        y += 40;
        const status = this.add.text(20, y, `Status: ${nodeData.status}`, { fontSize: '18px', fill: '#0f0' });
        panel.add(status);

        const closeButton = this.add.text(280, 10, 'X', { fontSize: '24px', fill: '#ff0000' }).setOrigin(0.5).setInteractive();
        closeButton.on('pointerdown', () => panel.destroy());
        panel.add(closeButton);

        this.inspectorPanel = panel;
    }

    handleCommandResponse(response) {
        if (response.data && response.data.type === 'file_content') {
            this.scene.launch('NotepadScene', { content: response.data.content });
        }
    }
}
