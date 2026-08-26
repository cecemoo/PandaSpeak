function urlBase64ToUint8Array(base64String) {

    const padding = "=".repeat((4 - base64String.length % 4) % 4);

    const base64 = (base64String + padding)

        .replace(/-/g, "+")

        .replace(/_/g, "/");

    const rawData = window.atob(base64);

    return Uint8Array.from(

        [...rawData].map(char => char.charCodeAt(0))

    );

}

async function enablePushNotifications() {
    try {
        if (!("serviceWorker" in navigator)) {
            alert("Push notifications are not supported in this browser.");
            return;
        }
        if (!("PushManager" in window)) {
            alert("Push notifications are not supported in this browser.");
            return;
        }
        const permission = await Notification.requestPermission();
        if (permission !== "granted") {
            alert("Notification permission was not granted.");
            return;
        }
        await navigator.serviceWorker.register(
            "/service-worker.js",
            {
                scope: "/"
            }
        );

        const registration = await navigator.serviceWorker.ready;
        if (!window.VAPID_PUBLIC_KEY) {
            console.error("VAPID public key is missing.");
            alert("Push notification public key is missing.");
            return;
        }
        console.log("VAPID public key:", window.VAPID_PUBLIC_KEY);
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(
                window.VAPID_PUBLIC_KEY
            )

        });

        const response = await fetch("/push/subscribe/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(subscription)
        });
        const result = await response.json();
        if (result.success) {
            alert("PandaSpeak notifications are enabled.");
            updateNotificationButton();
        } else {
            alert("Unable to save notification subscription.");
        }
    } catch (error) {
        console.error(error);
        alert("Unable to enable notifications.");
    }
}

async function updateNotificationButton() {

    const button = document.getElementById("notificationButton");

    if (!button || !("serviceWorker" in navigator)) {

        return;

    }

    try {

        const registration = await navigator.serviceWorker.ready;

        const subscription =

            await registration.pushManager.getSubscription();

        if (subscription) {

            button.textContent = "Disable Notifications";

            button.classList.remove("btn-primary");

            button.classList.add("btn-secondary");

        } else {

            button.textContent = "Enable Notifications";

            button.classList.remove("btn-secondary");

            button.classList.add("btn-primary");

        }

    } catch (error) {

        console.error(

            "Unable to check notification status:",

            error

        );

    }

}

async function togglePushNotifications() {

    try {

        if (!("serviceWorker" in navigator)) {

            alert("Push notifications are not supported in this browser.");

            return;

        }

        const registration = await navigator.serviceWorker.ready;

        const subscription =

            await registration.pushManager.getSubscription();

        if (subscription) {
            const response = await fetch("/push/unsubscribe/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    endpoint: subscription.endpoint
                })
            });
            const result = await response.json();
            if (!result.success) {
                alert("Unable to disable notifications.");
                return;
            }
            await subscription.unsubscribe();
            alert("PandaSpeak notifications are disabled.");
            await updateNotificationButton();
        } else {
            await enablePushNotifications();
        }

    } catch (error) {
        console.error(error);
        alert("Unable to change notification settings.");
    }

}



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {
    updateNotificationButton();
});