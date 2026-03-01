# 📦 File Storage Configuration Guide

## 🚨 **IMPORTANT: Why This Matters for Deployment**

When you deploy to platforms like **Render** or **Railway**, the default local file storage **WILL NOT WORK** properly because:

1. **Ephemeral Storage**: Files are deleted when the service restarts
2. **No Persistence**: Files don't survive redeployments
3. **Scaling Issues**: Multiple instances can't share files

## ✅ **Solution: Use Cloud Storage**

You have 3 options for production deployment:

---

## 🌟 **Option 1: Supabase Storage (Recommended)**

### Why Supabase?
- ✅ **Free tier**: 1 GB storage
- ✅ **Easy setup**: Already using Supabase for database
- ✅ **Built-in CDN**: Fast file delivery
- ✅ **Automatic backups**: Included
- ✅ **Simple API**: Easy to use

### Setup Steps:

#### 1. Create Supabase Storage Bucket

1. Go to your Supabase project dashboard: https://app.supabase.com
2. Click **"Storage"** in the left sidebar
3. Click **"Create a new bucket"**
4. Fill in:
   - **Name**: `resumes`
   - **Public**: ✅ Check **"Make bucket public"** (so users can access their files)
   - Click **"Create bucket"**

#### 2. Set Bucket Policies (Optional - for private files)

If you want files to be **private** (only accessible to authenticated users):

1. Go to **Storage** → **Policies** → Click your `resumes` bucket
2. Click **"New Policy"**
3. Choose **"Get access to authenticated users only"**
4. Save the policy

#### 3. Configure Environment Variables

Add these to your **Render** environment variables:

```bash
# File Storage Configuration
FILE_STORAGE_TYPE=supabase
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_BUCKET_NAME=resumes
```

> Get your `SUPABASE_URL` and `SUPABASE_KEY` from:
> Supabase Dashboard → Settings → API

#### 4. Test It!

Once deployed, upload a resume through your website. The file will:
- ✅ Be stored in Supabase Storage
- ✅ Persist across restarts
- ✅ Be accessible via public URL

---

## ☁️ **Option 2: AWS S3**

### Why S3?
- ✅ Industry standard
- ✅ Extremely reliable
- ✅ Free tier: 5 GB storage, 20K GET requests/month
- ✅ Scalable

### Setup Steps:

#### 1. Create S3 Bucket

1. Go to AWS Console → S3: https://s3.console.aws.amazon.com
2. Click **"Create bucket"**
3. Fill in:
   - **Bucket name**: `linkedin-automation-resumes-yourname` (must be globally unique)
   - **Region**: Choose closest to your Render region
   - **Block Public Access**: Uncheck (if you want public files) OR keep checked and use presigned URLs
   - Click **"Create bucket"**

#### 2. Create IAM User

1. Go to AWS Console → IAM: https://console.aws.amazon.com/iam
2. Click **"Users"** → **"Create user"**
3. Username: `linkedin-automation-uploader`
4. Click **"Next"** → **"Attach policies directly"**
5. Search for and select: **`AmazonS3FullAccess`** (or create custom policy)
6. Click **"Create user"**
7. Click on the user → **"Security credentials"** → **"Create access key"**
8. Choose **"Application running on AWS compute service"** → **"Create access key"**
9. **SAVE** the Access Key ID and Secret Access Key!

#### 3. Configure Environment Variables

Add these to **Render**:

```bash
# File Storage Configuration
FILE_STORAGE_TYPE=s3
AWS_S3_BUCKET_NAME=linkedin-automation-resumes-yourname
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=us-east-1
```

#### 4. Install boto3 (if not already installed)

Add to `requirements.txt`:
```
boto3==1.35.0
```

---

## 🏢 **Option 3: Local Storage (Development Only)**

### ⚠️ **WARNING**: DO NOT USE FOR PRODUCTION

Local storage on Render **WILL** cause issues:
- ❌ Files deleted on restart
- ❌ Files lost on redeploy
- ❌ No sharing between instances

### When to Use:
- ✅ Local development only
- ✅ Testing
- ✅ Quick demos

### Configuration:

```bash
FILE_STORAGE_TYPE=local
```

---

## 📊 **Comparison**

| Feature | Supabase | AWS S3 | Local |
|---------|----------|--------|-------|
| **Free Tier** | 1 GB | 5 GB | Unlimited |
| **Persistence** | ✅ Yes | ✅ Yes | ❌ No |
| **Setup Difficulty** | 🟢 Easy | 🟡 Medium | 🟢 Easy |
| **Cost (after free)** | $0.021/GB | $0.023/GB | Free |
| **Recommended for** | Production | Production | Dev only |
| **Public URLs** | ✅ Built-in | ✅ Available | ❌ No |
| **CDN** | ✅ Included | 🟡 Separate | ❌ No |

---

## 🚀 **Quick Start: Deploy with Supabase Storage**

### Step-by-step:

1. **Create Supabase bucket** (2 minutes):
   ```
   Dashboard → Storage → Create bucket → Name: "resumes" → Public
   ```

2. **Get credentials** (1 minute):
   ```
   Dashboard → Settings → API → Copy URL and anon key
   ```

3. **Set Render environment variables** (2 minutes):
   ```
   FILE_STORAGE_TYPE=supabase
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGc...
   SUPABASE_BUCKET_NAME=resumes
   ```

4. **Redeploy** (5 minutes):
   ```
   Render automatically redeploys when you save env vars
   ```

5. **Test** (1 minute):
   ```
   Upload a resume → Check Supabase Storage → File should appear!
   ```

**Total time: ~10 minutes** ✅

---

## 🔍 **How to Verify It's Working**

After deployment:

1. **Upload a resume** through your website
2. **Check Render logs**:
   ```
   Look for: "☁️ File saved to Supabase: resumes/xxxxx_resume.pdf"
   OR: "📁 File saved locally: uploads/xxxxx_resume.pdf"
   ```
3. **Check Supabase Storage**:
   - Go to Storage → resumes bucket
   - You should see your uploaded file
4. **Access the public URL**:
   - File URL format: `https://xxxxx.supabase.co/storage/v1/object/public/resumes/filename.pdf`

---

## 🆘 **Troubleshooting**

### Issue: "Files disappear after restart"
**Solution**: You're using local storage. Switch to Supabase or S3.

### Issue: "Supabase upload failed"
**Solution**: 
1. Check environment variables are set correctly
2. Check Supabase bucket exists and is accessible
3. Check `supabase` package is installed: `pip install supabase`

### Issue: "S3 access denied"
**Solution**:
1. Check IAM user has S3 permissions
2. Check AWS credentials are correct
3. Check bucket policy allows uploads

### Issue: "Local storage works in development but not production"
**Solution**: This is expected! Use Supabase or S3 for production.

---

## 💡 **Best Practices**

1. ✅ **Always use cloud storage for production**
2. ✅ **Keep local storage for development only**
3. ✅ **Store file paths in database, not the files themselves**
4. ✅ **Use environment variables for credentials**
5. ✅ **Set up file size limits** (already configured: 10 MB)
6. ✅ **Validate file types** (already configured: PDF, DOCX, TXT)
7. ✅ **Consider file cleanup/deletion after X days**
8. ✅ **Monitor storage usage** to avoid hitting limits

---

## 📖 **For Developers**

The file storage system is located in:
```
backend/utils/file_storage.py
```

It automatically:
- ✅ Detects storage type from `FILE_STORAGE_TYPE` env var
- ✅ Falls back to local storage if cloud storage fails
- ✅ Generates unique filenames to avoid collisions
- ✅ Returns both file path and public URL
- ✅ Supports async file operations

Usage in your code:
```python
from backend.utils.file_storage import file_storage

# Upload file
file_path, public_url = await file_storage.save_upload(
    file=uploaded_file,
    subfolder="resumes",
    user_id=user_id
)

# Retrieve file
file_content = await file_storage.get_file(file_path)

# Delete file
success = await file_storage.delete_file(file_path)
```

---

**🎉 You're all set! Your files will now persist in production!**
