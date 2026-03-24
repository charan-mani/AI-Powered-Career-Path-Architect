import React from 'react';
import { Link } from 'react-router-dom';
import {
  FiGithub,
  FiTwitter,
  FiLinkedin,
  FiMail,
  FiHeart,
  FiArrowUpRight,
  FiChevronRight,
} from 'react-icons/fi';
import { HiOutlineSparkles } from 'react-icons/hi';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const socialLinks = [
    { icon: FiGithub, href: 'https://github.com', label: 'GitHub', color: 'hover:bg-[#333]' },
    { icon: FiTwitter, href: 'https://twitter.com', label: 'Twitter', color: 'hover:bg-[#1DA1F2]' },
    { icon: FiLinkedin, href: 'https://linkedin.com', label: 'LinkedIn', color: 'hover:bg-[#0A66C2]' },
    { icon: FiMail, href: 'mailto:hello@careerarchitect.com', label: 'Email', color: 'hover:bg-[#EA4335]' },
  ];

  const quickLinks = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Roadmaps', path: '/roadmap' },
    { name: 'Skills', path: '/skills' },
    { name: 'Jobs', path: '/jobs' },
    { name: 'Analytics', path: '/analytics' },
  ];

  const supportLinks = [
    { name: 'Help Center', path: '/help' },
    { name: 'Contact', path: '/contact' },
    { name: 'Privacy', path: '/privacy' },
    { name: 'Terms', path: '/terms' },
  ];

  const resourcesLinks = [
    { name: 'Blog', path: '/blog' },
    { name: 'Guides', path: '/guides' },
    { name: 'FAQ', path: '/faq' },
  ];

  return (
    <footer className="relative bg-gradient-to-b from-gray-900 to-gray-950 text-gray-300 border-t border-gray-800/50">
      {/* Decorative gradient line */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Main Footer Content - 4-column layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 py-12">
          
          {/* Brand Column */}
          <div className="space-y-4">
            <Link to="/" className="flex items-center space-x-2 group">
              <div className="w-9 h-9 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/30 transition-all">
                <HiOutlineSparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="text-lg font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                  CareerArchitect
                </span>
                <span className="block text-[10px] text-gray-500 tracking-wider">AI-POWERED</span>
              </div>
            </Link>
            
            <p className="text-xs text-gray-400 leading-relaxed max-w-xs">
              Transform your career with AI-driven insights, personalized roadmaps, and intelligent job matching.
            </p>
            
            <div className="flex items-center space-x-2 pt-2">
              {socialLinks.map((social, index) => (
                <a
                  key={index}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 bg-gray-800/50 text-gray-400 hover:text-white rounded-lg border border-gray-700/50 hover:border-gray-600 transition-all duration-200 group"
                  aria-label={social.label}
                >
                  <social.icon className="w-4 h-4 group-hover:scale-110 transition-transform" />
                </a>
              ))}
            </div>
          </div>

          {/* Quick Links Column */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center">
              <span className="w-1 h-4 bg-indigo-500 rounded-full mr-2"></span>
              Quick Links
            </h3>
            <ul className="space-y-2.5">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className="text-sm text-gray-400 hover:text-white flex items-center group transition-colors"
                  >
                    <FiChevronRight className="w-3 h-3 mr-2 text-gray-600 group-hover:text-indigo-400 transition-colors" />
                    <span className="group-hover:translate-x-1 transition-transform duration-200">
                      {link.name}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Support Column */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center">
              <span className="w-1 h-4 bg-purple-500 rounded-full mr-2"></span>
              Support
            </h3>
            <ul className="space-y-2.5">
              {supportLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className="text-sm text-gray-400 hover:text-white flex items-center group transition-colors"
                  >
                    <FiChevronRight className="w-3 h-3 mr-2 text-gray-600 group-hover:text-purple-400 transition-colors" />
                    <span className="group-hover:translate-x-1 transition-transform duration-200">
                      {link.name}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Column */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center">
              <span className="w-1 h-4 bg-pink-500 rounded-full mr-2"></span>
              Resources
            </h3>
            <ul className="space-y-2.5">
              {resourcesLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className="text-sm text-gray-400 hover:text-white flex items-center group transition-colors"
                  >
                    <FiChevronRight className="w-3 h-3 mr-2 text-gray-600 group-hover:text-pink-400 transition-colors" />
                    <span className="group-hover:translate-x-1 transition-transform duration-200">
                      {link.name}
                    </span>
                  </Link>
                </li>
              ))}
              
              {/* Newsletter Signup */}
              <li className="pt-4">
                <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700/50">
                  <p className="text-xs text-gray-300 font-medium mb-2">Stay Updated</p>
                  <div className="flex">
                    <input
                      type="email"
                      placeholder="Your email"
                      className="flex-1 px-3 py-2 bg-gray-900/50 border border-gray-700 rounded-l-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    />
                    <button className="px-3 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-medium rounded-r-lg hover:from-indigo-700 hover:to-purple-700 transition-all">
                      Join
                    </button>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar - Sophisticated grey-black */}
        <div className="relative py-6 border-t border-gray-800">
          {/* Background pattern */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-gray-800/20 to-transparent"></div>
          
          <div className="relative flex flex-col md:flex-row justify-between items-center space-y-3 md:space-y-0">
            <div className="flex items-center space-x-4">
              <p className="text-xs text-gray-500">
                © {currentYear} CareerArchitect. All rights reserved.
              </p>
              <span className="text-gray-700">•</span>
              <p className="text-xs text-gray-600">
                v2.0.1
              </p>
            </div>
            
            <div className="flex items-center space-x-6">
              <Link to="/privacy" className="text-xs text-gray-500 hover:text-gray-300 transition-colors">
                Privacy
              </Link>
              <Link to="/terms" className="text-xs text-gray-500 hover:text-gray-300 transition-colors">
                Terms
              </Link>
              <Link to="/cookies" className="text-xs text-gray-500 hover:text-gray-300 transition-colors">
                Cookies
              </Link>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-600">Made with</span>
              <FiHeart className="w-3 h-3 text-red-500/70 animate-pulse" />
              <span className="text-xs text-gray-600">for your career growth</span>
            </div>
          </div>

          {/* Status indicators */}
          <div className="flex justify-center mt-3 space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-[10px] text-gray-600">All systems operational</span>
            </div>
            <span className="text-gray-700">|</span>
            <div className="flex items-center space-x-1">
              <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full"></div>
              <span className="text-[10px] text-gray-600">AI services active</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;