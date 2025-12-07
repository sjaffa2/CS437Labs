package com.example.hoavision;

import static java.lang.System.console;
import static java.lang.System.in;

import android.app.Dialog;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Intent;
import android.content.SharedPreferences;
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
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

public class ReportActivity extends AppCompatActivity implements View.OnClickListener{

    static String user;

    /**
     * Initializes the login activity, sets up the database helper, and registers click listeners.
     *
     * @param savedInstanceState If the activity is being re-initialized after previously being
     *                          shut down, this contains the data it most recently supplied.
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_report);
        user = getIntent().getStringExtra("username");
        SharedPreferences prefs = getSharedPreferences("MyGlobalPrefs", MODE_PRIVATE);
        Set<String> violationList = prefs.getStringSet(user, new HashSet<>());
        TextView myTextView = findViewById(R.id.textViewReport);
        System.out.println("yoohoo");
        System.out.println(violationList);
        String s = "";
        if(!violationList.isEmpty()){
            for(String v : violationList){
                s += (v + "\n");
            }
            myTextView.setText(s);
        }

        else myTextView.setText("No Violations!");
        System.out.println(s);



    }

    @Override
    public void onClick(View view) {
        Intent intent;

    }


}
