"use client";

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Loader2 } from 'lucide-react';

interface AuthGuardProps {
  children: React.ReactNode;
  // 允许未登录访问的路径
  publicPaths?: string[];
}

// 默认公开路径
const DEFAULT_PUBLIC_PATHS = ['/login', '/register', '/'];

export function AuthGuard({ 
  children, 
  publicPaths = DEFAULT_PUBLIC_PATHS 
}: AuthGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    // 等待认证状态加载完成
    if (isLoading) return;

    const isPublicPath = publicPaths.some(path => 
      pathname === path || pathname.startsWith(path + '/')
    );

    // 未登录且访问非公开路径，重定向到登录页
    if (!isAuthenticated && !isPublicPath) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, pathname, router, publicPaths]);

  // 加载中显示 Loading
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
      </div>
    );
  }

  // 未登录访问非公开路径，返回 null（等待重定向）
  const isPublicPath = publicPaths.some(path => 
    pathname === path || pathname.startsWith(path + '/')
  );
  
  if (!isAuthenticated && !isPublicPath) {
    return null;
  }

  return <>{children}</>;
}

// 用于页面级别的简化守卫 Hook
export function useAuthGuard(requireAuth: boolean = true) {
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuth();

  useEffect(() => {
    if (isLoading) return;

    if (requireAuth && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, requireAuth, router]);

  return { isAuthenticated, isLoading, user };
}
