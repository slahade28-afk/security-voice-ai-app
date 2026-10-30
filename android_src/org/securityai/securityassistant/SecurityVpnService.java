package org.securityai.securityassistant;

import android.content.Intent;
import android.net.VpnService;
import android.os.ParcelFileDescriptor;

public class SecurityVpnService extends VpnService {

    private ParcelFileDescriptor vpnInterface;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null) {
            stopSelf();
            return START_NOT_STICKY;
        }

        String action = intent.getAction();

        if ("STOP_FIREWALL".equals(action)) {
            stopVpn();
            stopSelf();
            return START_NOT_STICKY;
        }

        if ("BLOCK_ALL".equals(action)) {
            startBlocking();
        }

        return START_NOT_STICKY;
    }

    private void startBlocking() {
        if (vpnInterface != null) {
            return;
        }

        try {
            Builder builder = new Builder();
            builder.setSession("Security Assistant Firewall");
            builder.addAddress("10.23.0.1", 32);
            builder.addRoute("0.0.0.0", 0);
            builder.addAddress("fd23:4567::1", 128);
            builder.addRoute("::", 0);

            vpnInterface = builder.establish();

            if (vpnInterface == null) {
                stopSelf();
            }
        } catch (Exception e) {
            stopVpn();
            stopSelf();
        }
    }

    private void stopVpn() {
        if (vpnInterface != null) {
            try {
                vpnInterface.close();
            } catch (Exception ignored) {
            }
            vpnInterface = null;
        }
    }

    @Override
    public void onDestroy() {
        stopVpn();
        super.onDestroy();
    }
}
