def is_admin(user):
	return user.is_active, user.is_superuser, user.is_staff
