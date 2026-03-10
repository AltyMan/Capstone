class User {
  final int user_id;

  User({
    required this.user_id
  });

  factory User.fromJson(Map<String, dynamic> json) {
  return User(
    user_id: json['id'],
  );
  }

  Map<String, String> toQuery() {
    return {
        'user_id': user_id.toString(),
  };
  }
}
