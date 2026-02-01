import { useState } from "react";
import { Button, Flex, Card, Text, Heading, Badge } from "@radix-ui/themes";
import { InfoCircledIcon, CheckCircledIcon, ExclamationTriangleIcon, CrossCircledIcon } from "@radix-ui/react-icons";

type NotificationType = 'info' | 'success' | 'warning' | 'error';

interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
}

interface NotificationCenterProps {
  notifications: Notification[];
  onMarkAsRead: (id: string) => void;
  onClearAll: () => void;
  onDelete: (id: string) => void;
}

export function NotificationCenter({ 
  notifications, 
  onMarkAsRead, 
  onClearAll, 
  onDelete 
}: NotificationCenterProps) {
  const getIcon = (type: NotificationType) => {
    switch (type) {
      case 'info':
        return <InfoCircledIcon style={{ color: 'var(--blue-9)' }} />;
      case 'success':
        return <CheckCircledIcon style={{ color: 'var(--green-9)' }} />;
      case 'warning':
        return <ExclamationTriangleIcon style={{ color: 'var(--yellow-9)' }} />;
      case 'error':
        return <CrossCircledIcon style={{ color: 'var(--red-9)' }} />;
    }
  };

  const getTypeColor = (type: NotificationType) => {
    switch (type) {
      case 'info':
        return 'blue';
      case 'success':
        return 'green';
      case 'warning':
        return 'yellow';
      case 'error':
        return 'red';
    }
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <Card style={{ maxWidth: '400px' }}>
      <Flex direction="column" gap="4" p="4">
        <Flex justify="between" align="center">
          <Flex align="center" gap="2">
            <Heading size="5">Notifications</Heading>
            {unreadCount > 0 && (
              <Badge color="red" variant="solid">
                {unreadCount}
              </Badge>
            )}
          </Flex>
          <Button size="2" variant="ghost" onClick={onClearAll}>
            Clear All
          </Button>
        </Flex>

        {notifications.length === 0 ? (
          <Text color="gray" size="2" style={{ textAlign: 'center', padding: '20px' }}>
            No notifications
          </Text>
        ) : (
          <Flex direction="column" gap="3">
            {notifications.map((notification) => (
              <Card
                key={notification.id}
                variant={notification.read ? "surface" : "classic"}
                style={{
                  cursor: 'pointer',
                  borderLeft: `3px solid var(--${getTypeColor(notification.type)}-9)`
                }}
                onClick={() => onMarkAsRead(notification.id)}
              >
                <Flex gap="3" p="3">
                  <Flex style={{ minWidth: '20px' }}>
                    {getIcon(notification.type)}
                  </Flex>
                  <Flex direction="column" gap="1" style={{ flex: 1 }}>
                    <Flex justify="between" align="start">
                      <Text weight="medium" size="2">
                        {notification.title}
                      </Text>
                      <Text size="1" color="gray">
                        {formatTime(notification.timestamp)}
                      </Text>
                    </Flex>
                    <Text size="2" color="gray">
                      {notification.message}
                    </Text>
                    <Flex justify="between" align="center" mt="2">
                      <Badge 
                        size="1" 
                        color={getTypeColor(notification.type)} 
                        variant="soft"
                      >
                        {notification.type}
                      </Badge>
                      <Button
                        size="1"
                        variant="ghost"
                        color="red"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(notification.id);
                        }}
                      >
                        Delete
                      </Button>
                    </Flex>
                  </Flex>
                </Flex>
              </Card>
            ))}
          </Flex>
        )}
      </Flex>
    </Card>
  );
}

// Sample hook for managing notifications
export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      type: 'success',
      title: 'Project Created',
      message: 'Your new project has been successfully created.',
      timestamp: new Date(Date.now() - 5 * 60000), // 5 minutes ago
      read: false,
    },
    {
      id: '2',
      type: 'warning',
      title: 'Storage Almost Full',
      message: 'You have used 85% of your storage quota.',
      timestamp: new Date(Date.now() - 30 * 60000), // 30 minutes ago
      read: false,
    },
    {
      id: '3',
      type: 'info',
      title: 'New Feature Available',
      message: 'Check out the new dashboard analytics features.',
      timestamp: new Date(Date.now() - 2 * 60 * 60000), // 2 hours ago
      read: true,
    },
  ]);

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false,
    };
    setNotifications(prev => [newNotification, ...prev]);
  };

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };

  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  return {
    notifications,
    addNotification,
    markAsRead,
    deleteNotification,
    clearAll,
  };
}
