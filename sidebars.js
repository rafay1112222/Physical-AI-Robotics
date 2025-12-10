// sidebars.js

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  textbookSidebar: [
    // Part I: Foundations of Physical AI
    {
      type: 'category',
      label: 'Part I: Foundations of Physical AI',
      link: { type: 'generated-index', title: 'Physical AI Fundamentals', description: 'Introduction to embodied intelligence, basic concepts, and foundational technologies.' },
      items: [
        {
          type: 'doc',
          id: 'Introduction_physical_ai',
          label: 'Introduction'
        },
        'chapter_1_foundations'
      ],
    },
    // Part II: Robotic Middleware and Digital Twins
    {
      type: 'category',
      label: 'Part II: Robotic Middleware and Digital Twins',
      link: { type: 'generated-index', title: 'Middleware and Simulation', description: 'ROS 2 architecture and digital twin platforms for robotics.' },
      items: ['chapter_2_ros2_fundamentals', 'chapter_3_digital_twin'],
    },
    // Part III: AI Platforms and Control
    {
      type: 'category',
      label: 'Part III: AI Platforms and Control',
      link: { type: 'generated-index', title: 'AI Control Systems', description: 'Advanced AI platforms and control systems for humanoid robots.' },
      items: ['chapter_4_nvidia_isaac', 'chapter_5_humanoid_development'],
    },
    // Part IV: Conversational AI and Future Directions
    {
      type: 'category',
      label: 'Part IV: Conversational AI and Future Directions',
      link: { type: 'generated-index', title: 'Advanced Interaction', description: 'Conversational robotics and Vision-Language-Action frameworks.' },
      items: ['chapter_6_conversational_robotics'],
    },
  ],
};

module.exports = sidebars;