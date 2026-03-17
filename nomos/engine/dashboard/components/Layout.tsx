import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const [user, setUser] = useState({ name: 'Dr. Scholar', role: 'Scholar' });

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    { href: '/corrections', label: 'Corrections', icon: '✏️' },
    { href: '/audit_log', label: 'Audit Log', icon: '📋' },
    { href: '/conflict_resolution', label: 'Conflicts', icon: '⚖️' },
    { href: '/analytics', label: 'Analytics', icon: '📈' },
    { href: '/transparency_report', label: 'Transparency', icon: '👁️' },
  ];

  const isActive = (href: string) => router.pathname === href;

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="sidebar fixed h-screen">
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-2xl font-bold text-quranic-gold">NOMOS</h1>
          <p className="text-gray-400 text-sm">Scholar Governance</p>
        </div>

        {/* Navigation */}
        <nav className="mt-8">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href}>
              <div
                className={`px-6 py-3 flex items-center cursor-pointer transition ${
                  isActive(item.href)
                    ? 'bg-quranic-gold text-quranic-dark font-semibold'
                    : 'hover:bg-gray-800'
                }`}
              >
                <span className="mr-3">{item.icon}</span>
                <span>{item.label}</span>
              </div>
            </Link>
          ))}
        </nav>

        {/* User Profile */}
        <div className="absolute bottom-0 w-full border-t border-gray-700 p-6">
          <div className="flex items-center">
            <div className="w-10 h-10 rounded-full bg-quranic-gold flex items-center justify-center">
              <span className="text-quranic-dark font-bold">
                {user.name.charAt(0)}
              </span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-semibold">{user.name}</p>
              <p className="text-xs text-gray-400">{user.role}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </div>
    </div>
  );
}
