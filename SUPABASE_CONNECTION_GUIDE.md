# Supabase Connection Guide

## Current Status
✅ Network connectivity: Working
✅ Supabase API credentials: Configured
⚠️ PostgreSQL connection: Needs correct connection string from your dashboard

## To Get the Correct PostgreSQL Connection String:

1. **Go to your Supabase Dashboard**:
   - Visit: https://app.supabase.com
   - Log in to your account

2. **Select your project**: `xaaglooqmwzhitwdlcnz`

3. **Get the Connection String**:
   - Click on "Project Settings" (gear icon in left sidebar)
   - Click on "Database" tab
   - Scroll to "Connection string"
   - Select "URI" format
   - Copy the connection string

4. **The connection string should look like**:
   ```
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
   OR for direct connection:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

5. **Update your `.env` file**:
   - Replace `SUPABASE_DATABASE_URL` with the correct connection string from dashboard
   - Make sure to URL-encode special characters in the password:
     - `@` becomes `%40`
     - `#` becomes `%23`
     - `&` becomes `%26`
     - etc.

## Current Configuration

Your current settings:
- ✅ SUPABASE_URL: https://xaaglooqmwzhitwdlcnz.supabase.co
- ✅ SUPABASE_KEY: Configured (Anon key)
- ⚠️ SUPABASE_DATABASE_URL: Needs update from dashboard

## Alternative: Use Supabase REST API (Recommended for Now)

Since the PostgreSQL connection requires the exact connection string from your dashboard,
you can use the Supabase REST API which is already working:

```python
# For now, keep using SQLite for your app
DATABASE_URL=sqlite:///./data/autoagenthire.db

# For Supabase operations, you'll use the REST API
# (Once the Python SDK issues are resolved)
```

## Test Commands

After updating the connection string:
```bash
python test_supabase_simple.py
```

## Notes

- Your app is fully functional with SQLite
- Supabase REST API credentials are configured
- Only the direct PostgreSQL connection needs the correct string from dashboard
- The error "Tenant or user not found" means the username format is incorrect

