cat vendor/xiaomi/camera/proprietary/system/priv-app/MiuiCamera/MiuiCamera.apk.part* > vendor/xiaomi/camera/proprietary/system/priv-app/MiuiCamera/MiuiCamera.apk

# Camera patches
echo 'Applying MIUI camera patches'
cd frameworks/base
wget https://raw.githubusercontent.com/AOSP-for-vili/vili-patches/refs/heads/main/memecam/0001-camera-Add-backwards-compatible-CaptureResultExtras-.patch
wget https://raw.githubusercontent.com/AOSP-for-vili/vili-patches/refs/heads/main/memecam/0002-core-camera2-StreamConfigurationMap-add-constructor-.patch

PATCH1="0001-camera-Add-backwards-compatible-CaptureResultExtras-.patch"
PATCH2="0002-core-camera2-StreamConfigurationMap-add-constructor-.patch"
# Tries to apply the first patch
if git am "$PATCH1"; then
    echo "First patch applied successfully"
    # Only applies if the first was successful
    git am "$PATCH2"
    echo "Second patch applied successfully"
else
    echo "Failed to apply the first patch. Either already applied or ran into conflicts. Aborting..."
    git am --abort
    cd ../..
    return 1 2>/dev/null || exit 1
fi

cd ../..
