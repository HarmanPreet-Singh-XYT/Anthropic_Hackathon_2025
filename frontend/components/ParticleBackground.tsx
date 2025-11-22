import { motion } from 'framer-motion';

export function ParticleBackground() {
    const particles = Array.from({ length: 30 }, (_, i) => ({
        id: i,
        left: `${Math.random() * 100}%`,
        delay: Math.random() * 5,
        duration: 10 + Math.random() * 10,
        size: 2 + Math.random() * 4,
    }));

    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {particles.map((particle) => (
                <motion.div
                    key={particle.id}
                    className="absolute bottom-0 bg-white rounded-full"
                    style={{
                        left: particle.left,
                        width: particle.size,
                        height: particle.size,
                    }}
                    animate={{
                        y: [0, -900],
                        x: [0, (Math.random() - 0.5) * 200],
                        opacity: [0, 1, 1, 0],
                        scale: [0, 1, 1, 0],
                    }}
                    transition={{
                        duration: particle.duration,
                        delay: particle.delay,
                        repeat: Infinity,
                        ease: "linear",
                    }}
                />
            ))}
        </div>
    );
}
