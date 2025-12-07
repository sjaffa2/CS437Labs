package com.example.hoavision;

import android.app.Dialog;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Intent;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.net.Uri;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

import android.util.Log;
import android.view.View;

//import androidx.navigation.ui.AppBarConfiguration;
//
//import edu.uiuc.cs427app.data.DBHelper;
//import edu.uiuc.cs427app.databinding.ActivityLoginBinding;

import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Spinner;
import android.widget.Toast;

import java.util.ArrayList;
public class LoginActivity extends AppCompatActivity implements View.OnClickListener{

    private RadioGroup radioGroup;
    private RadioButton hoaAdmin, house1, house2, house3;
    /**
     * Initializes the login activity, sets up the database helper, and registers click listeners.
     *
     * @param savedInstanceState If the activity is being re-initialized after previously being
     *                          shut down, this contains the data it most recently supplied.
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        //helper = new DBHelper(this, "mydb", null, 1);

        Button buttonNew = findViewById(R.id.buttonLogin);

        buttonNew.setOnClickListener(this);

        radioGroup = findViewById(R.id.radioGroup);
        hoaAdmin = findViewById(R.id.hoaAdmin);
        house1 = findViewById(R.id.house1);
        house2 = findViewById(R.id.house2);
        house3 = findViewById(R.id.house3);

    }

    /**
     * Handles click events for login and sign up buttons.
     * For login button, validates user credentials and navigates to main activity.
     * For sign up button, displays the sign up dialog.
     *
     * @param view The view that was clicked.
     */
    @Override
    public void onClick(View view) {
        Intent intent;
        // Determine which theme is selected
        int selectedTheme;
        int selectedId = radioGroup.getCheckedRadioButtonId();
        if (selectedId == R.id.hoaAdmin) {
            goToMainActivity();
        } else if (selectedId == R.id.house1) {
            goToReportActivity("House1");
        } else if (selectedId == R.id.house2) {
            goToReportActivity("House2");
        } else if (selectedId == R.id.house3) {
            goToReportActivity("House3");
        } else {
            goToReportActivity("House1");
        }
    }
    private void goToMainActivity() {
        Intent intent = new Intent(this, MainActivity.class);
        startActivity(intent);
    }
    private void goToReportActivity(String userName) {
        Intent intent = new Intent(this, ReportActivity.class);
        intent.putExtra("username", userName);
        startActivity(intent);
    }
}
