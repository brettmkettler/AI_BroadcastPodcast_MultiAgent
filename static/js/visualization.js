// P5.js sketch for avatar visualization
let host1Sketch = new p5((p) => {
    let particles = [];
    const numParticles = 50;

    p.setup = () => {
        const canvas = p.createCanvas(200, 200);
        canvas.parent('host1-avatar');
        for (let i = 0; i < numParticles; i++) {
            particles.push(new Particle(p));
        }
    };

    p.draw = () => {
        p.background(61, 61, 61);
        particles.forEach(particle => {
            particle.update();
            particle.display();
        });
    };
}, 'host1-avatar');

let host2Sketch = new p5((p) => {
    let particles = [];
    const numParticles = 50;

    p.setup = () => {
        const canvas = p.createCanvas(200, 200);
        canvas.parent('host2-avatar');
        for (let i = 0; i < numParticles; i++) {
            particles.push(new Particle(p));
        }
    };

    p.draw = () => {
        p.background(61, 61, 61);
        particles.forEach(particle => {
            particle.update();
            particle.display();
        });
    };
}, 'host2-avatar');

class Particle {
    constructor(p) {
        this.p = p;
        this.pos = p.createVector(p.random(p.width), p.random(p.height));
        this.vel = p.createVector(p.random(-1, 1), p.random(-1, 1));
        this.size = p.random(3, 8);
        this.color = p.color(p.random(100, 255), p.random(100, 255), p.random(100, 255));
    }

    update() {
        this.pos.add(this.vel);
        
        if (this.pos.x < 0 || this.pos.x > this.p.width) {
            this.vel.x *= -1;
        }
        if (this.pos.y < 0 || this.pos.y > this.p.height) {
            this.vel.y *= -1;
        }
    }

    display() {
        this.p.noStroke();
        this.p.fill(this.color);
        this.p.circle(this.pos.x, this.pos.y, this.size);
    }
}
