// sidebars.js

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    // Part I: Fundamentals of Physical AI
    {
      type: 'category',
      label: 'Part I: Fundamentals of Physical AI',
      link: { type: 'generated-index', title: 'Physical AI Fundamentals', description: 'Introduction to embodied intelligence, kinematics, and core sensing technologies.' },
      items: ['intro', 'chapter2_kinematics', 'chapter3_sensing'],
    },
    // Part II: The Humanoid Form and Actuation
    {
      type: 'category',
      label: 'Part II: The Humanoid Form and Actuation',
      link: { type: 'generated-index', title: 'Humanoid Systems', description: 'Deep dive into humanoid biomechanics, specialized actuators, and manipulation.' },
      items: ['chapter4_humanoid_kinematics', 'chapter5_actuators', 'chapter6_manipulation'],
    },
    // Part III: AI and Learning for Physical Systems
    {
      type: 'category',
      label: 'Part III: AI and Learning for Physical Systems',
      link: { type: 'generated-index', title: 'AI Control and Perception', description: 'Middleware, advanced learning, computer vision, and human interaction protocols.' },
      items: ['chapter7_ros', 'chapter8_rl', 'chapter9_vision'],
    },
    // Part IV: Case Studies and Future Directions
    {
      type: 'category',
      label: 'Part IV: Case Studies and Future Directions',
      link: { type: 'generated-index', title: 'Applications and Ethics', description: 'Review of real-world platforms and the ethical roadmap for humanoid robots.' },
      items: ['chapter11_platforms', 'chapter12_ethics'],
    },
  ],
};

module.exports = sidebars;