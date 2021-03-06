# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import BaseTest

from stored_messages import mark_read, add_message_for, broadcast_message, mark_all_read
from stored_messages.models import Inbox, MessageArchive

from stored_messages.compat import get_user_model
import stored_messages


class TestApi(BaseTest):
    def test_mark_as_read(self):
        self.client.login(username='test_user', password='123456')
        self.client.get('/create')
        inbox = Inbox.objects.filter(user=self.user)
        self.assertEqual(len(inbox), 1)
        mark_read(self.user, inbox.get().message)
        self.assertEqual(Inbox.objects.filter(user=self.user).count(), 0)

    def test_mark_as_read_idempotent(self):
        self.client.login(username='test_user', password='123456')
        self.client.get('/create')
        msg = MessageArchive.objects.filter(user=self.user).get()
        self.assertTrue(mark_read(self.user, msg))
        self.assertFalse(mark_read(self.user, msg))

    def test_add_message_for(self):
        user2 = get_user_model().objects.create_user("another_user", "u@user.com", "123456")
        add_message_for([user2, self.user], stored_messages.STORED_ERROR, 'Multiple errors')
        self.assertEqual(Inbox.objects.count(), 2)
        self.assertEqual(MessageArchive.objects.count(), 2)

        self.assertEqual(Inbox.objects.get(user=user2.id).message.message, "Multiple errors")
        self.assertEqual(Inbox.objects.get(user=self.user).message.message, "Multiple errors")

        self.assertEqual(MessageArchive.objects.get(user=user2.id).message.message,
                         "Multiple errors")
        self.assertEqual(MessageArchive.objects.get(user=self.user).message.message,
                         "Multiple errors")

    def test_broadcast_message(self):
        self.assertRaises(NotImplementedError,
                          broadcast_message,
                          stored_messages.STORED_INFO, 'one ☢ for all')

    def test_mark_all_read(self):
        for i in range(20):
            stored_messages.add_message_for([self.user], stored_messages.INFO, "unicode message ❤")
        inbox = Inbox.objects.filter(user=self.user)
        self.assertEqual(len(inbox), 20)
        mark_all_read(self.user)
        self.assertEqual(Inbox.objects.filter(user=self.user).count(), 0)
