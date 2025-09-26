# Firehouse Movers Landing Page

A React-based landing page for Firehouse Movers, built with modern web technologies and animations.

## Features

- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Smooth Animations**: GSAP-powered animations for enhanced user experience
- **Modern UI**: Clean, professional design matching the original Django template
- **Interactive Elements**: Hover effects and scroll-triggered animations
- **Service Showcase**: Comprehensive display of all company services

## Technologies Used

- **React 18**: Modern React with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **GSAP**: Professional-grade animations
- **Font Awesome**: Icon library
- **Responsive Design**: Mobile-first approach

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn

### Installation

1. Navigate to the project directory:
   ```bash
   cd react-landing
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Building for Production

```bash
npm run build
```

This builds the app for production to the `build` folder.

## Project Structure

```
src/
├── components/
│   ├── Header.js          # Navigation header
│   ├── Hero.js            # Hero section with truck animation
│   ├── PlatformStatement.js # Company mission statement
│   ├── ServicesOverview.js  # Services overview section
│   ├── ServicesGrid.js    # Detailed services grid
│   ├── LoginPrompt.js     # Call-to-action section
│   └── Footer.js          # Footer with contact info
├── App.js                 # Main application component
├── App.css               # Global styles
└── index.js              # Application entry point
```

## Key Features

### Hero Section
- Animated truck SVG with GSAP animations
- Responsive text with strong visual hierarchy
- Background image with overlay effects

### Services Grid
- Interactive service cards with hover effects
- Categorized service sections
- Smooth scroll-triggered animations

### Navigation
- Responsive header with mobile menu
- Smooth transitions and hover effects
- Logo and branding consistency

### Animations
- GSAP-powered scroll animations
- Truck movement and wheel rotation
- Service card entrance animations
- Smooth hover transitions

## Customization

### Adding New Services
Edit the `ServicesGrid.js` component to add new service cards:

```javascript
const newService = {
  id: 12,
  title: "New Service",
  description: "Service description",
  image: "/images/new-service.jpg",
  link: "/new-service",
  category: "NEW",
  icon: <YourIconComponent />
};
```

### Styling
- Global styles: `src/App.css`
- Component-specific styles: `src/components/*.css`
- Tailwind configuration: `tailwind.config.js`

## Deployment

The built application can be deployed to any static hosting service:

- **Netlify**: Drag and drop the `build` folder
- **Vercel**: Connect your GitHub repository
- **AWS S3**: Upload the `build` folder contents
- **GitHub Pages**: Use the `gh-pages` package

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary to Firehouse Movers Inc.
