import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
//import 'package:google_sign_in/google_sign_in.dart';

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  //final GoogleSignIn googleSignIn = GoogleSignIn();

  // Sign in with email and password
  Future<User?> signIn(String email, String password) async {
    try {
      UserCredential result = await _auth.signInWithEmailAndPassword(email: email, password: password);
      return result.user;
    } catch (error) {
      return null;
    }
  }

  // Register with email and password and username
  Future<User?> register(String email, String password, String username) async {
    try {
      UserCredential result = await _auth.createUserWithEmailAndPassword(email: email, password: password);
      await result.user!.updateDisplayName(username);
      await result.user!.updatePhotoURL("https://st3.depositphotos.com/9998432/13335/v/450/depositphotos_133351928-stock-illustration-default-placeholder-man-and-woman.jpg");
      await _firestore.collection('users').doc(result.user!.uid).set({'username': username});
      return result.user;
    } catch (error) {
      return null;
    }
  }

  // Sign out
  Future<void> signOut() async {
    /*
    if (googleSignIn.currentUser != null) {
      await googleSignIn.signOut();
    }
    */
    await _auth.signOut();
  }

  // Get the current user
  User? getCurrentUser() {
    return _auth.currentUser;
  }

  Future<DocumentSnapshot> getCurrentUserDetails() async {
    return await _firestore.collection('users').doc(getCurrentUser()!.uid).get();
  }



  /*
  Future<User?> signInWithGoogle() async {
    try {
      final GoogleSignInAccount? googleSignInAccount = await googleSignIn.signIn();
      if (googleSignInAccount != null) {
        final GoogleSignInAuthentication googleSignInAuthentication = await googleSignInAccount.authentication;
        final AuthCredential credential = GoogleAuthProvider.credential(
          accessToken: googleSignInAuthentication.accessToken,
          idToken: googleSignInAuthentication.idToken,
        );
        final UserCredential authResult = await _auth.signInWithCredential(credential);
        return authResult.user;
      }
    } catch (error) {
      print(error);
      return null;
    }
    return null;
  }
  */

}