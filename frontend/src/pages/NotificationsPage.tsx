import { Flex, Heading, Text, Card, Button } from '@radix-ui/themes';
import { NotificationCenter, useNotifications } from '@/components/NotificationCenter';

export function NotificationsPage() {
  const {
    notifications,
    addNotification,
    markAsRead,
    deleteNotification,
    clearAll,
  } = useNotifications();

  return (
    <Flex direction="column" gap="6">
      <Heading size="8">Notification Center</Heading>
      <Text color="gray">
        This shows a notification center with different types of notifications, timestamps, and interaction capabilities.
        Notifications can be marked as read, deleted individually, or cleared all at once.
      </Text>
      
      <Flex gap="4" align="start">
        <NotificationCenter
          notifications={notifications}
          onMarkAsRead={markAsRead}
          onClearAll={clearAll}
          onDelete={deleteNotification}
        />
        
        <Card style={{ flex: 1 }}>
          <Flex direction="column" gap="3" p="4">
            <Heading size="5">Test Notifications</Heading>
            <Text size="2" color="gray">
              Click these buttons to add different types of notifications and test the notification system:
            </Text>
            <Flex direction="column" gap="2">
              <Button 
                onClick={() => addNotification({
                  type: 'info',
                  title: 'Information',
                  message: 'This is an informational message with useful details.'
                })}
                variant="soft"
                color="blue"
              >
                Add Info Notification
              </Button>
              <Button 
                onClick={() => addNotification({
                  type: 'success',
                  title: 'Operation Successful',
                  message: 'Your operation has been completed successfully!'
                })}
                variant="soft"
                color="green"
              >
                Add Success Notification
              </Button>
              <Button 
                onClick={() => addNotification({
                  type: 'warning',
                  title: 'Warning',
                  message: 'Please review your settings before proceeding.'
                })}
                variant="soft"
                color="yellow"
              >
                Add Warning Notification
              </Button>
              <Button 
                onClick={() => addNotification({
                  type: 'error',
                  title: 'Error Occurred',
                  message: 'Something went wrong. Please try again or contact support.'
                })}
                variant="soft"
                color="red"
              >
                Add Error Notification
              </Button>
            </Flex>
            
            <Text size="2" color="gray" style={{ marginTop: '16px' }}>
              <Text weight="medium">Features:</Text><br />
              • Real-time notifications<br />
              • Multiple notification types<br />
              • Mark as read functionality<br />
              • Individual deletion<br />
              • Clear all notifications<br />
              • Timestamp display<br />
              • Unread count badge
            </Text>
          </Flex>
        </Card>
      </Flex>
    </Flex>
  );
}
