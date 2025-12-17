'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  FolderGit2, 
  Briefcase, 
  LayoutTemplate,
  Plus,
  Github,
  LogOut,
  Settings,
  Menu,
  User
} from 'lucide-react';
import { ProjectsList } from '@/components/dashboard/projects-list';
import { JobsList } from '@/components/dashboard/jobs-list';
import { ResumesList } from '@/components/dashboard/resumes-list';
import { TemplatesList } from '@/components/dashboard/templates-list';
import { ProfileView } from '@/components/dashboard/profile-view';
import { useToast } from '@/hooks/use-toast';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('resumes');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();

  // Handle OAuth callback params
  useEffect(() => {
    const github = searchParams.get('github');
    const token = searchParams.get('token');
    const error = searchParams.get('error');

    if (github === 'connected') {
      if (token) {
        localStorage.setItem('token', token);
        toast({ title: 'GitHub connected!', description: 'Your account is now linked.' });
      } else {
        toast({ title: 'GitHub connected!', description: 'Authorization successful.' });
      }
      router.replace('/dashboard');
    }

    if (error) {
      toast({ 
        title: 'GitHub connection failed', 
        description: `Error: ${error.replace(/_/g, ' ')}`,
        variant: 'destructive'
      });
      router.replace('/dashboard');
    }
  }, [searchParams, router, toast]);

  // Load current user info
  useEffect(() => {
    const loadUser = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          router.push('/login');
          return;
        }
        
        const response = await fetch('http://localhost:8000/api/auth/profile', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
          const userData = await response.json();
          setCurrentUser(userData);
        } else if (response.status === 401) {
          localStorage.removeItem('token');
          router.push('/login');
        }
      } catch (error) {
        console.error('Failed to load user:', error);
      }
    };
    
    loadUser();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    toast({ title: 'Logged out successfully' });
    router.push('/login');
  };

  const handleGithubConnect = () => {
    const clientId = 'Ov23li7PyDbHv0U1oqbZ';
    const redirectUri = encodeURIComponent('http://localhost:3000/api/auth/callback/github');
    const scope = encodeURIComponent('read:user user:email repo');
    const authUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
    console.log('Redirecting to GitHub OAuth:', authUrl);
    window.location.href = authUrl;
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-16'} border-r bg-card transition-all duration-200 relative`}>
        <div className="p-4 border-b flex items-center justify-between">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <FileText className="h-6 w-6" />
              <span className="font-bold">Resume Agent</span>
            </div>
          )}
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <Menu className="h-5 w-5" />
          </Button>
        </div>
        
        <nav className="p-2 space-y-1">
          <SidebarItem 
            icon={<FileText className="h-5 w-5" />} 
            label="Resumes" 
            active={activeTab === 'resumes'}
            onClick={() => setActiveTab('resumes')}
            collapsed={!sidebarOpen}
          />
          <SidebarItem 
            icon={<FolderGit2 className="h-5 w-5" />} 
            label="Projects" 
            active={activeTab === 'projects'}
            onClick={() => setActiveTab('projects')}
            collapsed={!sidebarOpen}
          />
          <SidebarItem 
            icon={<Briefcase className="h-5 w-5" />} 
            label="Job Descriptions" 
            active={activeTab === 'jobs'}
            onClick={() => setActiveTab('jobs')}
            collapsed={!sidebarOpen}
          />
          <SidebarItem 
            icon={<LayoutTemplate className="h-5 w-5" />} 
            label="Templates" 
            active={activeTab === 'templates'}
            onClick={() => setActiveTab('templates')}
            collapsed={!sidebarOpen}
          />
        </nav>
        
        <div className="absolute bottom-0 left-0 right-0 p-2 border-t bg-card">
          <SidebarItem 
            icon={<User className="h-5 w-5" />} 
            label="Profile" 
            active={activeTab === 'profile'}
            onClick={() => setActiveTab('profile')}
            collapsed={!sidebarOpen}
          />
          <SidebarItem 
            icon={<Settings className="h-5 w-5" />} 
            label="Settings" 
            onClick={() => setShowSettings(true)}
            collapsed={!sidebarOpen}
          />
          <SidebarItem 
            icon={<LogOut className="h-5 w-5" />} 
            label="Logout" 
            onClick={handleLogout}
            collapsed={!sidebarOpen}
          />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Header */}
        <header className="border-b bg-card p-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold capitalize">{activeTab}</h1>
            <p className="text-muted-foreground">
              {activeTab === 'resumes' && 'Manage and generate your resumes'}
              {activeTab === 'projects' && 'Your imported projects and repositories'}
              {activeTab === 'jobs' && 'Job descriptions to tailor resumes to'}
              {activeTab === 'templates' && 'LaTeX templates for your resumes'}
              {activeTab === 'profile' && 'View and edit your profile information'}
            </p>
          </div>
          <div className="flex gap-3 items-center">
            {currentUser && (
              <div className="text-sm text-right mr-2">
                <p className="font-medium">{currentUser.name || currentUser.email}</p>
                <p className="text-xs text-muted-foreground">{currentUser.email}</p>
              </div>
            )}
            <Button variant="outline" className="gap-2" onClick={handleGithubConnect}>
              <Github className="h-4 w-4" />
              Connect GitHub
            </Button>
          </div>
        </header>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'resumes' && <ResumesList />}
          {activeTab === 'projects' && <ProjectsList />}
          {activeTab === 'jobs' && <JobsList />}
          {activeTab === 'templates' && <TemplatesList />}
          {activeTab === 'profile' && <ProfileView />}
        </div>
      </main>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowSettings(false)}>
          <Card className="w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <CardHeader>
              <CardTitle>Profile Settings</CardTitle>
              <CardDescription>Manage your account settings and upload resume for auto-fill</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <p className="text-sm font-medium">Upload Resume</p>
                <p className="text-xs text-muted-foreground">Upload your existing resume to auto-fill profile fields</p>
                <input
                  type="file"
                  id="resume-upload"
                  accept=".pdf,.docx,.doc,.txt"
                  className="hidden"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (!file) return;

                    const formData = new FormData();
                    formData.append('file', file);

                    try {
                      const token = localStorage.getItem('token');
                      const response = await fetch('http://localhost:8000/api/auth/upload-resume', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` },
                        body: formData,
                      });

                      const data = await response.json();
                      if (response.ok) {
                        toast({ 
                          title: 'Resume uploaded!', 
                          description: `Successfully extracted ${data.fields_updated} profile fields. Check the Profile tab!` 
                        });
                        // Reload user data to show updated name
                        const userResponse = await fetch('http://localhost:8000/api/auth/profile', {
                          headers: { 'Authorization': `Bearer ${token}` }
                        });
                        if (userResponse.ok) {
                          const userData = await userResponse.json();
                          setCurrentUser(userData);
                        }
                        setShowSettings(false);
                      } else {
                        toast({ 
                          title: 'Upload failed', 
                          description: data.detail || 'Could not process resume',
                          variant: 'destructive'
                        });
                      }
                    } catch (error) {
                      toast({ 
                        title: 'Upload error', 
                        description: 'Failed to upload resume',
                        variant: 'destructive'
                      });
                    }
                    e.target.value = '';
                  }}
                />
                <Button 
                  variant="outline" 
                  className="w-full gap-2" 
                  onClick={() => document.getElementById('resume-upload')?.click()}
                >
                  <FileText className="h-4 w-4" />
                  Upload Resume (PDF/DOCX/TXT)
                </Button>
              </div>
              
              <div className="space-y-2 pt-2 border-t">
                <p className="text-sm font-medium">GitHub Integration</p>
                <Button variant="outline" className="w-full gap-2" onClick={handleGithubConnect}>
                  <Github className="h-4 w-4" />
                  Connect GitHub Account
                </Button>
              </div>
              
              <div className="pt-4 border-t">
                <Button variant="destructive" className="w-full" onClick={handleLogout}>
                  Logout
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

function SidebarItem({
  icon,
  label,
  active = false,
  onClick,
  collapsed = false,
}: {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  onClick: () => void;
  collapsed?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
        active 
          ? 'bg-primary text-primary-foreground' 
          : 'hover:bg-muted text-muted-foreground hover:text-foreground'
      }`}
    >
      {icon}
      {!collapsed && <span>{label}</span>}
    </button>
  );
}
