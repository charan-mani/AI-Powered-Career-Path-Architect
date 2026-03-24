import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Navbar from './Navbar';
import Footer from './Footer';
import { useAuth } from '../../hooks/useAuth';

const Layout = () => {
  const { user } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Check screen size on resize
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 1024);
      // Auto-close mobile menu when resizing to desktop
      if (window.innerWidth >= 1024) {
        setIsMobileMenuOpen(false);
      }
    };
    
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
      {/* Header with mobile menu toggle passed via context or prop */}
      <Header 
        onMobileMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        isMobileMenuOpen={isMobileMenuOpen}
      />
      
      <div className="flex flex-1 relative">
        {/* Desktop Sidebar Navigation - Hidden on mobile, visible on lg screens */}
        {user && (
          <div className="hidden lg:block w-64 flex-shrink-0">
            <Navbar />
          </div>
        )}
        
        {/* Mobile Sidebar Overlay */}
        {user && isMobileMenuOpen && (
          <>
            {/* Backdrop */}
            <div 
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
              onClick={() => setIsMobileMenuOpen(false)}
            />
            
            {/* Mobile Sidebar - Slides in from left */}
            <div className="fixed left-0 top-0 h-full w-72 z-50 lg:hidden animate-slide-in">
              <Navbar 
                isMobile={true}
                onClose={() => setIsMobileMenuOpen(false)}
              />
            </div>
          </>
        )}
        
        {/* Main Content - Responsive padding */}
        <main className={`flex-1 w-full transition-all duration-300 ${
          user && !isMobile ? 'lg:ml-0' : ''
        }`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
            <Outlet />
          </div>
        </main>
      </div>

      <Footer />
    </div>
  );
};

export default Layout;