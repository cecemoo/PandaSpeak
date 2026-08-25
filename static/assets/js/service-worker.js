self.addEventListener("push", function (event) {

    let data = {};

    if (event.data) {

        data = event.data.json();

    }

    const title = data.title || "PandaSpeak";

    const options = {

        body: data.body || "You have a new notification.",

        icon: "/static/img/favicon.png",

        badge: "/static/img/favicon.png",

        data: {

            url: data.url || "/"

        }

    };

    event.waitUntil(

        self.registration.showNotification(title, options)

    );

});

self.addEventListener("notificationclick", function (event) {

    event.notification.close();

    const url = event.notification.data.url || "/";

    event.waitUntil(

        clients.openWindow(url)

    );

});